import wx
import calendar
from pprint import pformat
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Any

import wx._core

from logger import logger, _
from config import load_config
from utils import (
    csv_to_dict,
    convert_docx_template_to_pdf,
    number_to_words_currency,
)


@dataclass
class DocTemplate:
    label: str
    name: str
    path: Path
    prefix: str


class NumericTextCtrl(wx.TextCtrl):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        value: str = "",
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = 0,
        validator: wx.Validator = wx.DefaultValidator,
        name: str = wx.TextCtrlNameStr,
    ) -> None:
        super(NumericTextCtrl, self).__init__(
            parent, id, value, pos, size, style, validator, name
        )
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def OnChar(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > wx.WXK_START:
            event.Skip()
            return
        if chr(key).isdigit():
            event.Skip()
            return
        return


class AppFrame(wx.Frame):
    def __init__(self, *args: Any, **kw: dict[str, Any]) -> None:
        super(AppFrame, self).__init__(*args, **kw)

        self.SetWindowStyle(
            wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )

        self.load_config()
        self.set_app_settings()

        self.set_app_variables()

        self.load_doc_templates()
        self.load_executors()

        self.set_app_frame()

    def load_config(self) -> None:
        self.config = load_config()
        for path in [
            self.config["DATA_DIR"],
            self.config["DATA_PATH"],
            self.config["DOC_TEMPLATES_DIR"],
            self.config["PDF_DIR"],
        ]:
            if path.exists():
                continue
            elif path.is_file():
                self.log(
                    text=_('File "{path}" not found').format(path=path),
                    level="error",
                    show_msg=True,
                    msg_caption=_("Error"),
                    msg_style=wx.OK | wx.ICON_ERROR,
                )
            else:
                self.log(
                    text=_('Directory "{path}" not found').format(path=path),
                    level="error",
                    show_msg=True,
                    msg_caption=_("Error"),
                    msg_style=wx.OK | wx.ICON_ERROR,
                )
            self.Close()
            return

    def set_app_variables(self) -> None:
        self.app_variables = {
            "DOC_TEMPLATE_LABEL",
            "DOC_TEMPLATE_NAME",
            "DOC_TEMPLATE_PREFIX",
            "DATE_DAY",
            "DATE_MONTH_LABEL",
            "DATE_MONTH",
            "DATE_YEAR",
            "EXECUTOR_LABEL",
            "DOC_NUM",
            "AMOUNT",
            "AMOUNT_INT",
            "AMOUNT_TEXT",
        }
        self.log(_("App variables ready"))
        logger.debug(
            "App variables:\n{app_variables}".format(
                app_variables=pformat(self.app_variables)
            )
        )

    def load_doc_templates(self) -> None:
        self.doc_templates: dict[str, DocTemplate] = {}
        for label, name, prefix in self.config["DOC_TEMPLATES_FILES"]:
            path = self.config["DOC_TEMPLATES_DIR"] / name
            if not path.exists():
                self.log(
                    text=_('File "{path}" not found').format(path=path),
                    level="error",
                    show_msg=True,
                    msg_caption=_("Error"),
                    msg_style=wx.OK | wx.ICON_ERROR,
                )
                self.Close()
                return
            self.doc_templates[label] = DocTemplate(
                label=label,
                name=name,
                path=path,
                prefix=prefix,
            )
        self.log(
            _("Templates loaded: {doc_templates}").format(
                doc_templates=len(self.doc_templates)
            )
        )

    def load_executors(self) -> None:
        try:
            self.executors = csv_to_dict(
                csv_path=self.config["DATA_PATH"],
                wrong_headers=self.app_variables,
            )
        except ValueError as e:
            wx.MessageBox(
                f"{e}",
                _("Error"),
                wx.OK | wx.ICON_ERROR,
            )
            logger.error(_("Invalid headers: {e}").format(e=e))
            self.Close()
            self.executors = {}
            return
        self.log(
            _("Executors is loaded: {count}").format(
                count=len(self.executors),
            )
        )
        logger.debug(
            "Executors:\n{executors}".format(executors=pformat(self.executors))
        )

    def on_about(self, event: wx.CommandEvent) -> None:
        wx.MessageBox(
            f"{self.config['PROJECT_NAME']} v.{self.config['PROJECT_VERSION']}",
            _("About"),
            wx.OK | wx.ICON_INFORMATION,
        )

    def on_replaceable_fields(self, event: wx.CommandEvent) -> None:
        content = "FROM GUI:\n\n"
        for field in self.app_variables:
            content += f"[{field}]\n"
        content += "\nFROM HEADERS:\n\n"
        for header in list(self.executors.values())[0].keys():
            content += f"[{header}]\n"
        wx.MessageBox(
            content,
            _("Replaceable fields"),
            wx.OK | wx.ICON_INFORMATION,
        )

    def open_file(self, filepath: Path, label: str | None = None) -> None:
        filename = label or filepath.name
        if not filepath.exists():
            filepath = filepath.parent.parent / filepath.name
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                dlg = wx.MessageDialog(
                    self, content, filename, wx.OK | wx.ICON_INFORMATION
                )
                dlg.ShowModal()
                dlg.Destroy()
        else:
            wx.MessageBox(
                _("File {filename} not found").format(filename=filename),
                _("Error"),
                wx.OK | wx.ICON_ERROR,
            )

    def on_license(self, event: wx.CommandEvent) -> None:
        self.open_file(Path(__file__).parent / "LICENSE", _("License"))

    def on_notice(self, event: wx.CommandEvent) -> None:
        self.open_file(Path(__file__).parent / "NOTICE", _("Notice"))

    def set_app_frame(self) -> None:
        self.log(_("UI initialized"))

        menubar = wx.MenuBar()

        about_menu = wx.Menu()

        about_item = about_menu.Append(wx.ID_ANY, _("About"))
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

        license_item = about_menu.Append(wx.ID_ANY, _("License"))
        self.Bind(wx.EVT_MENU, self.on_license, license_item)

        notice_item = about_menu.Append(wx.ID_ANY, _("Notice"))
        self.Bind(wx.EVT_MENU, self.on_notice, notice_item)

        replaceable_fields_item = about_menu.Append(
            wx.ID_ANY, _("Replaceable fields")
        )
        self.Bind(
            wx.EVT_MENU,
            self.on_replaceable_fields,
            replaceable_fields_item,
        )

        menubar.Append(about_menu, _("About"))
        self.SetMenuBar(menubar)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        date_sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(
            wx.StaticText(panel, label=_("Document type:")), 0, wx.ALL, 5
        )
        self.doc_template_choice = wx.Choice(
            panel, choices=list(self.doc_templates.keys())
        )
        sizer.Add(self.doc_template_choice, 0, wx.ALL | wx.EXPAND, 5)
        doctype_help = wx.StaticText(panel, label=_("Document type help"))
        doctype_help.SetForegroundColour(wx.RED)
        sizer.Add(doctype_help, 0, wx.ALL, 5)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        self.log(_("Document type - added"))

        sizer.Add(
            wx.StaticText(panel, label=_("Date:")),
            0,
            wx.ALL,
            5,
        )
        self.month_choiceses = [
            _("january"),
            _("february"),
            _("march"),
            _("april"),
            _("may"),
            _("june"),
            _("july"),
            _("august"),
            _("september"),
            _("october"),
            _("november"),
            _("december"),
        ]
        # current_year = str(datetime.datetime.now().year)
        years = [
            str(i)
            for i in range(
                self.config["DATE_YEAR_MIN"], self.config["DATE_YEAR_MAX"] + 1
            )
        ]
        # self.day_choice.SetItems([str(i).zfill(2) for i in range(1, 32)])
        self.day_choice = wx.Choice(
            panel, choices=[str(i).zfill(2) for i in range(1, 32)]
        )
        self.month_choice = wx.Choice(panel, choices=self.month_choiceses)
        self.year_choice = wx.Choice(panel, choices=years)
        # self.month_choice.Bind(wx.EVT_CHOICE, self.update_days)
        # self.year_choice.Bind(wx.EVT_CHOICE, self.update_days)
        date_sizer.Add(self.day_choice, 0, wx.ALL, 5)
        date_sizer.Add(self.month_choice, 0, wx.ALL, 5)
        date_sizer.Add(self.year_choice, 0, wx.ALL, 5)
        sizer.Add(date_sizer, 0, wx.ALL, 0)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        self.log(_("Date - added"))

        sizer.Add(wx.StaticText(panel, label=_("Executor:")), 0, wx.ALL, 5)
        self.executor_choice = wx.Choice(
            panel, choices=list(self.executors.keys())
        )
        sizer.Add(self.executor_choice, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        self.log(_("Executor - added"))

        sizer.Add(
            wx.StaticText(panel, label=_("Document number:")),
            0,
            wx.ALL,
            5,
        )
        self.billnum_input = NumericTextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.billnum_input, 0, wx.ALL | wx.EXPAND, 5)
        billnum_input_help = wx.StaticText(
            panel, label=_("only numbers allowed")
        )
        billnum_input_help.SetForegroundColour(wx.RED)
        sizer.Add(billnum_input_help, 0, wx.ALL, 5)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        self.log(_("Document number - added"))

        sizer.Add(wx.StaticText(panel, label=_("Amount:")), 0, wx.ALL, 5)
        self.price_input = NumericTextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sizer.Add(self.price_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 5)
        self.log(_("Amount - added"))

        self.button = wx.Button(panel, label=_("Create PDF"))
        self.button.Bind(wx.EVT_BUTTON, self.on_button_click)
        sizer.Add(self.button, 0, wx.ALL | wx.EXPAND, 10)
        self.log(_("Button created"))

        panel.SetSizer(sizer)
        self.log(_("UI created"))

    def set_app_settings(self) -> None:
        self.SetSize((300, 550))

        title = f"{self.config['PROJECT_NAME']} | v.{self.config['PROJECT_VERSION']}"
        self.SetTitle(title)
        self.CreateStatusBar()

    def show_msg(self, message: str, caption: str, style: int) -> None:
        wx.MessageBox(message, caption, style)

    def log(
        self,
        text: str,
        level: Literal["info", "debug", "error"] = "info",
        set_status: bool = True,
        write_log: bool = True,
        show_msg: bool = False,
        msg_message: str | None = None,
        msg_caption: str = _("Information"),
        msg_style: int = wx.OK | wx.ICON_INFORMATION,
    ) -> None:
        if set_status:
            try:
                self.SetStatusText(text)
            except wx._core.wxAssertionError:
                pass
        if write_log:
            log_method = getattr(logger, level)
            log_method(text)
        if not self.config["SHOW_MESSAGES"]:
            return
        if show_msg and not msg_message:
            self.show_msg(text, msg_caption, msg_style)
        elif msg_message:
            self.show_msg(msg_message, msg_caption, msg_style)

    def on_button_click(self, event: wx.CommandEvent) -> None:
        logger.debug("Button clicked")
        if not self.is_fields_valid():
            return

        wx.CallAfter(
            self.log,
            text=_("Please wait..."),
            show_msg=True,
        )
        wx.CallLater(1000, self.convert_document)

    def convert_document(self) -> None:
        self.log(_("Converting document"))
        replacement_words = self.get_replacement_words()
        pdf_file_name = self.config["PDF_NAME_MASK"].format(**self.config)
        pdf_file_path = self.config["PDF_DIR"] / pdf_file_name
        convert_docx_template_to_pdf(
            docx_template_path=self.config["DOC_TEMPLATE_PATH"],
            pdf_file_path=pdf_file_path,
            replacement_words=replacement_words,
        )
        if pdf_file_path.exists():
            self.log(
                _("Conversion successful"),
                msg_message=_("File created: {file_name}").format(
                    file_name=pdf_file_name
                ),
                msg_caption=_("Success"),
            )
            self.log(
                _("Document created: {path}").format(path=pdf_file_path),
                "debug",
                set_status=False,
            )
            if self.config["FINISH_AFTER_SUCCESS"]:
                self.log(_("Application will be closed"))
                self.Close()
        else:
            self.log(
                _("Conversion failed"),
                msg_message=_("File not created"),
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )

    def is_fields_valid(self) -> bool:
        self.log(_("Validating fields"))
        doc_template = self.doc_template_choice.GetStringSelection()
        if doc_template:
            self.config["DOC_TEMPLATE_LABEL"] = doc_template
            self.config["DOC_TEMPLATE_NAME"] = self.doc_templates[
                doc_template
            ].name
            self.config["DOC_TEMPLATE_PATH"] = self.doc_templates[
                doc_template
            ].path
            self.config["DOC_TEMPLATE_PREFIX"] = self.doc_templates[
                doc_template
            ].prefix
        else:
            self.log(
                _("Document template not selected"),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        date_day = self.day_choice.GetStringSelection()
        date_month = self.month_choice.GetStringSelection()
        if date_month:
            date_month_num = self.month_choiceses.index(date_month) + 1
        date_year = self.year_choice.GetStringSelection()
        if date_day and date_month and date_year:
            self.config["DATE_DAY"] = date_day
            self.config["DATE_MONTH_LABEL"] = date_month
            self.config["DATE_MONTH"] = f"{date_month_num:02d}"
            self.config["DATE_YEAR"] = date_year
        else:
            self.log(
                _("Date not selected"),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        first_day, days_in_month = calendar.monthrange(
            int(date_year), date_month_num
        )
        good_days = [str(i).zfill(2) for i in range(1, days_in_month + 1)]
        current_day = date_day

        if current_day not in good_days:
            self.log(
                _("There are only {count} days in this month.").format(
                    count=len(good_days)
                ),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        executor_label = self.executor_choice.GetStringSelection()
        if executor_label:
            self.config["EXECUTOR_LABEL"] = executor_label
            self.config["EXECUTOR_DATA"] = self.executors[executor_label]
        else:
            self.log(
                _("Executor not selected"),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        if all(
            [
                self.billnum_input.GetValue(),
                re.match(r"^\d+$", self.billnum_input.GetValue()),
            ]
        ):
            self.config["DOC_NUM"] = self.billnum_input.GetValue()
        else:
            self.log(
                _("Document number not entered or entered incorrectly"),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        if all(
            [
                self.price_input.GetValue(),
                re.match(r"^\d+$", self.price_input.GetValue()),
            ]
        ):
            self.config["AMOUNT"] = self.price_input.GetValue()
            self.config["AMOUNT_INT"] = int(self.price_input.GetValue())
            self.config["AMOUNT_TEXT"] = number_to_words_currency(
                self.config["AMOUNT_INT"],
                self.config["CURRENCY_PLURALIZE"],
            ).capitalize()
        else:
            self.log(
                _("Amount not entered or entered incorrectly"),
                "error",
                show_msg=True,
                msg_caption=_("Error"),
                msg_style=wx.OK | wx.ICON_ERROR,
            )
            return False

        logger.debug("Config:\n{config}".format(config=pformat(self.config)))
        self.log(_("Validation passed"))

        return True

    def get_replacement_words(self) -> dict[str, str]:
        pairs = {}
        for name in self.app_variables:
            pairs[name] = self.config[name]  # type: ignore
        pairs |= self.config["EXECUTOR_DATA"]
        self.log(_("Fields to replaced is ready"))
        logger.debug("Replacing words:\n{pairs}".format(pairs=pformat(pairs)))
        return pairs


def run_app() -> None:
    logger.info(_("Application started"))
    app = wx.App()
    app_frame = AppFrame(None)
    app_frame.Show()
    app.MainLoop()
    logger.info(_("Application closed"))

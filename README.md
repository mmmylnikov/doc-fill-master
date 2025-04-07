# Doc Fill Master

This Python application is designed to fill `.docx` document templates using 
data provided via a graphical user interface (GUI). The user selects values 
for predefined fields, and the program replaces placeholders in `.docx` 
templates. The output is saved as `.pdf` files.

---

## Features

- **Support for Multiple Document Templates**: Create and fill templates for letters, invoices, or other documents.
- **Dynamic Field Replacement**: Replace placeholders, such as `[DOC_NUM]`, `[DATE_DAY]`, `[DATE_MONTH_LABEL]`, etc., with user-selected data.
- **CSV-Based Data Integration**: Automatically populate fields using external CSV files.
- **PDF Output**: Save the generated documents as `.pdf` files.
- **Multi-Language Support**: Use `pybabel` to translate the interface into multiple languages.

## Requirements

This project requires Python 3.12 or newer and the following dependencies, managed with [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). Attention: Document templates are converted to `pdf` format directly using Microsoft Word (must be installed).


## Usage

### 1. Setup

+ Clone this repository.

+ Install dependencies:

```sh
uv sync
```

+ Ensure that the templates (letter.docx, invoice.docx, etc.) are located in the `./src/templates/` directory.

+ Add any additional data to `./src/data/data.csv` (use `;` as the delimiter).

### 2. Run the Application

Start the GUI application:

```sh
uv run make app
```

### 3. Filling out templates
Select a document template (for example, letter or invoice).
Use the graphical interface to select or enter values for placeholders.
Create a document and save it as a pdf.

### 4. Localization

To support multiple languages:

+ Extract translation strings:

```sh
uv run make pybabel_extract
```

+ Initialize a new language (if your locale doesn't exist):

```sh
uv run make pybabel_init
```

+ Edit the messages.po file to include translations.

+ Compile translations:

```sh
uv run make pybabel_compile
```

### 5. Generate PDF Output

The filled `.docx` file will automatically be converted to `.pdf` when the user saves it.

## Example CSV Format

The `./src/data/data.csv` file should have the following structure:

```txt
RECIPIENT_NAME;RECIPIENT_ADDRESS;SERVICE_DESCRIPTION;MANAGER_NAME;COMPANY_NAME
John Doe;123 Fictional St, Imaginary City, ZZ;Consultation Services;Alice Johnson;Example Corp
Jane Roe;456 Nowhere Rd, Nonexistent Town, YY;Development Support;Chris Peterson;Demo Solutions
```

You can use labels of headers in your templates for replacing by format `[HEADER_LABEL]`. You also have access to some built-in GUI fields like `[DATE_DAY]` and `[DATE_MONTH_LABEL]`. You can see the available labels in the `Replacement fields` menu.


## Configuring Application Parameters

The application uses a configuration file written in `pyproject.toml` to manage various runtime settings. These parameters are located under the `[tool.doc_fill_master]` section and can be customized to adapt the application to your specific requirements. Below is a guide on each available parameter and how to modify it.

### Configurable Parameters

| Parameter |  Type | Default Value | Description |
|-----------|-------|---------------|-------------|
|language | String | "en" | The language for the application's interface ("en" for English, "ru" for Russian, etc.). |
| logging_level | String | "INFO" | The logging level for the application ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). |
| logging_to_file | Boolean | False | Enable logging to a file. |
| logging_file_name | String | "app.log" | The name of the logging file. |
| logging_file_dir | String | "." | The directory where the logging file will be saved. |
| data_dir | String | "./data" | The directory where the data files are located. |
| data_name | String | "data.csv" | The name of the data file. |
| doc_templates_dir | String | "./templates" | The directory where the document templates are located. |
| doc_templates_files | List of Tuples | [("letter", "letter.docx", "Letter №"), ("nvoice", "invoice.docx", "Invoice №")] | A list of tuples containing the label, name, and prefix for each document template. |
| pdf_dir | String | "./pdf" | The directory where the generated PDF files will be saved. |
| pdf_name_mask | String | "{DOC_TEMPLATE_PREFIX} {DOC_NUM}.pdf" | The mask for the PDF file name. |
| date_year_min | Integer | 2023 | The minimum year for date selection. |
| date_year_max | Integer | 2025 | The maximum year for date selection. |
| currency_pluralize | List of Strings | ["`$`", "`$`", "`$`"] | A list of strings representing the plural forms of the currency. |
| show_messages | Boolean | True | Enable or disable message display. |
| finish_after_success | Boolean | True | Close the application after successful document conversion. |


## How to Build a Standalone Executable with PyInstaller

You can compile the program into a single executable file using [PyInstaller](https://www.pyinstaller.org/).

### 1. Install PyInstaller

PyInstaller is already included in --dev project dependencies. You can install it using the following command: 

```sh
uv sync
```

### 2. Compile the Application

Run the following command to create a standalone executable:

```sh
uv run make build
```

### 3. Result

The compiled executable will be saved in the `./dist` directory.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

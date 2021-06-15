import os
import logging
import typer
from os import path
from flaskmicroservs_faro.server_entrypoint import execute


__version__ = "0.1.0"


# Declaring the typer application
app = typer.Typer()


def version_callback(value: bool):
    """ Callback of the version optional parameter """

    if value:
        typer.echo(f"Flask Server Launcher Microservs Version: {__version__}")


def check_file_not_exists_callback(file_path: str):
    """ Validation of files """

    if not path.exists(file_path):
        raise FileNotFoundError("File {} does not exist".format(file_path))

    return file_path


@app.command()
def format_file(
        flask_port: int = typer.Argument(
            ...),
        upload_folder: str = typer.Argument(
            ...),        
        version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True),):
    """ Analysing a new model

    FLASK_PORT -- port of the flask API
    UPLOAD_FOLDER -- folder to upload files in the server

    """
    typer.echo("Analysing a new file")

    execute(flask_port, upload_folder)

    
if __name__ == "__main__":

    """ Basic launch functionality """

    log_level = os.getenv('MICROSERVS_LOG_LEVEL', "INFO")
    log_file = os.getenv('MICROSERVS_LOG_FILE', None)

    handlers = [logging.StreamHandler()]
    if log_file is not None:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(name)20s: %(message)s",
        handlers=handlers)

    app()

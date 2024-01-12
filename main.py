import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator
from server import app

if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
    proxy = args.openai_proxy if args.openai_proxy else config['OpenAIModel']['proxy']
    model = OpenAIModel(model=model_name, api_key=api_key, proxy = proxy)


    to_lan = args.to_lan if args.to_lan else config['common']['to_lan']
    style = args.style if args.style else config['common']['style']
    pdf_file_path = args.book if args.book else config['common']['book']
    file_format = args.file_format if args.file_format else config['common']['file_format']
    rest_port = args.rest_port if args.rest_port else config['common']['rest_port']

    # 实例化 PDFTranslator 类，并调用 translate_pdf() 方法
    translator = PDFTranslator(model)
    print(rest_port)
    if rest_port == 0:
        translator.translate_pdf(pdf_file_path, file_format, to_lan, style)
    else:
        app.config.update({'translator': translator})
        app.run(port=rest_port)

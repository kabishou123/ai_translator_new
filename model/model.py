from book import ContentType

class Model:
    def make_text_messages(self, text: str, from_lan = "English", to_lan = "Chinese", style="plain") -> dict:
        prompt = self.make_text_prompt(text, from_lan, to_lan)
        messages = [
                {"role": "system", "content": "You are an expert in translation from {} to {}. The translation shall be in {} style.".format(from_lan, to_lan, style)},
                {"role": "user", "content": prompt}
            ]        
        return messages

    def make_table_messages(self, text: str, from_lan = "English", to_lan = "Chinese") -> dict:
        prompt = self.make_table_prompt(text, from_lan, to_lan)
        messages = [
                {"role": "system", "content": "You are an expert in translation from {} to {}. Output in table format and keep the delimeter and spacing.".format(from_lan, to_lan)},
                {"role": "user", "content": prompt}
            ]        
        return messages
    
    def make_text_prompt(self, text: str, from_lan = "English", to_lan = "Chinese", style = "plain") -> str:
        return f"Please translate：{text}"

    def make_table_prompt(self, table: str, from_lan = "English", to_lan = "Chinese", style = "plain") -> str:
        return table

    def translate_messages(self, content, from_lan = "English", to_lan = "Chinese", style = "plain") -> str:
        if content.content_type == ContentType.TEXT:
            return self.make_text_messages(content.get_original_as_str(), from_lan, to_lan, style)
        elif content.content_type == ContentType.TABLE:
            return self.make_table_messages(content.get_original_as_str(), from_lan, to_lan)
        else:
            return None

    def make_request(self, messages):
        raise NotImplementedError("子类必须实现 make_request 方法")

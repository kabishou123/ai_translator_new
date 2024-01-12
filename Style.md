# 加入风格
为了使翻译器支持风格（style），做了如下改动：
1. 配置文件引入style参数
2. restful api引入style参数
3. Gradio界面引入style输入（text）
4. Prompt支持风格


```
messages = [
                {"role": "system", "content": "You are an expert in translation from {} to {}. The translation shall be in {} style.".format(from_lan, to_lan, style)},
                {"role": "user", "content": prompt}
            ]
```


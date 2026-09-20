import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_post(topic: str, platform: str, tone: str) -> dict:
    system_prompt = (
        "Ты - ассистент для контент-мейкеров. "
        "Ты создаешь готовые посты для соцсетей на основе брифа пользователя. "
        "Отвечай строго в формате JSON с ключами 'post' и 'headlines' "
        "(headlines - список из 3 строк). "
    )

    user_prompt = (
        f"Тема : {topic}\n"
        f"Платформа: {platform}\n"
        f"Тон: {tone}\n\n"
        f"Напиши готовый пост под эту платформу и тон, "
        f"а также предложи 3 варианта заголовка/подписи. "
    )


    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     response_format={"type": "json_object"}
    # )
    # result_text = response.choices[0].message.content
    # return result_text


    mock_result = {
        "post": f"Встречайте: {topic}! Идеально подходит для {platform}, "
                f"сделано в {tone} тоне специально для вас ",
        "headlines": [
            f"{topic}: то, чего вы ждали",
            f"Новинка недели — {topic}",
            f"Почему все говорят про {topic}"
        ]
    }
    return mock_result


if __name__ == "__main__":
    result = generate_post("новая коллекция худи", "Instagram", "дружелюбный")
    print(result)
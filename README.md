# Oman_Explorer
This project is chat bot that uses LLM. This project was crated to be shared for the competition  "Engineer it with AI"

Python 3.11.4 

Set_up steps :
- download
  https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip
- Run the following command in ngrok
 ```  ngrok http 8000 --domain=adapting-moccasin-vastly.ngrok-free.app ```
- ``` git colne "https://github.com/Maram99Alhinai/Oman_Explorer.git" ```
- ``` python -m venv omanexplor ```
- ``` omanexplor\Scripts\activate ```
- ``` pip install -r requirements.txt ```

Steps to run:
- ``` Python main.py ```


### Directory
Oman_Explorer/

│

├── app/

│   ├── init.py

│   ├── config.py

│   ├── view.py

│   ├── decorators/

│   │   ├── security.py

│   ├── services/

│   │   ├── openai_service.py

│   │   └── db_service.py

│   ├── utils/

│   │   ├── init.py

│   │   ├── whatsapp_utils.py

│

├── requirements.txt

├── .env                      

├── .gitignore

├── main.py

├── README.md

└── LICENSE
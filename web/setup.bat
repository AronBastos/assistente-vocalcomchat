@echo off
echo 🔧 Configurando Ambiente do Assistente VocalCom...

echo 📦 Criando ambiente virtual...
python -m venv venv

echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate

echo 📥 Instalando dependências...
pip install --upgrade pip
pip install pyperclip==1.8.2

cd web
pip install Flask==2.3.3 Flask-CORS==4.0.0 Werkzeug==2.3.7

echo 📝 Criando requirements.txt...
echo Flask==2.3.3 > requirements.txt
echo Flask-CORS==4.0.0 >> requirements.txt
echo Werkzeug==2.3.7 >> requirements.txt
echo pyperclip==1.8.2 >> requirements.txt

cd ..

echo ✅ Configuração concluída!
echo 🚀 Execute: venv\Scripts\activate && cd web && python run.py
pause
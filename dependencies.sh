#some packages required to get things setup on the termux environment on the tablet 
#pkg install openssh
#pkg install git
#pkg update && pkg upgrade

#if needed to grab the most updated version
#git clone https://github.com/ShearerP1/departureboard.git
#cd departureboard

#set up the environment and install required packages
python -m venv venv
source venv/bin/activate
pip install flask requests pythjon-dotenv gunicorn tzdata
python tt.py

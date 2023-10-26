cd /tmp/
wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz
tar -xzvf Python-3.11.4.tgz
cd Python-3.11.4/

sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev

./configure --enable-optimizations

make -j `nproc`

sudo make altinstall

python3.11 -V

sudo ln -s /usr/local/bin/python3.11 /usr/local/bin/python
sudo ln -s /usr/local/bin/python3.11 /usr/local/bin/python3

python -VV
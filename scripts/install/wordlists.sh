#!/bin/bash
echo "Installing wordlists..."
sudo apt install wordlists;

echo "Installing rockyou.txt..."
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz;
#/usr/share/wordlists
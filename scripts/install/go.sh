rm -rf /usr/local/go;
tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz;
export PATH=$PATH:/usr/local/go/bin;
ln -s /usr/local/go/bin/go /usr/local/bin/go;
ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt;
go version;
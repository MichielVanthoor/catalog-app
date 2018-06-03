Catalog Application
=============
Steps to launch:

1. Install Vagrant and VirtualBox.
2. Clone this repository
3. Launch the Vagrant VM by typing `vagrant up` in terminal in the directory `/vagrant` in this repo
4. Update dependencies and install sqlite 3
    ```
    sudo apt-get update
    sudo apt-get install sqlite3 libsqlite3-dev
    ```
5. Run your application within the VM by typing `python /vagrant/catalog/application.py` into the terminal
6. Access by visiting http://localhost:5000 locally on your browser

Enjoy!

import os
import sys
import getopt

def main(argv):
   directory = ''
   host = ''
   try:
      opts, args = getopt.getopt(argv,"d:h:")
   except getopt.GetoptError:
      print ('test.py -d <project-directory> -h <V-Host-name>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '--h':
         print ('test.py -d <project-directory> -h <V-Host-name>')
         sys.exit()
      elif opt in ("-d", "--directory"):
         directory = arg
      elif opt in ("-h", "--host"):
         host = arg
   link_directory(directory)
   nginx_config_files(directory,host)
   write_host(host)
   restart_nginx()

def link_directory(directory):
   os.system('sudo ln -s '+directory+' /var/www')

def nginx_config_files(directory,host):
   config = """server {
    listen 80;
    server_name """ + host + """;
    root /var/www/""" + os.path.split(directory)[1]  + """/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";

    index index.html index.htm index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}"""
   host_config = open("/etc/nginx/sites-available/"+host,"w")
   host_config.write(config)
   host_config.close()
   os.system('sudo ln -s /etc/nginx/sites-available/'+host+' /etc/nginx/sites-enabled/')

def write_host(host):
   host_config = open("/etc/hosts","a")
   host_config.write("127.0.0.1       "+host+"\n")
   host_config.close()

def restart_nginx():
   os.system("sudo systemctl restart nginx.service ")
   
if __name__ == "__main__":
   main(sys.argv[1:])
   
import os
import shutil
import stat

from jinja2 import Environment, FileSystemLoader

from dotenv import load_dotenv

load_dotenv()

docker_instances = int(os.environ.get('DOCKER_INSTANCES'))
token = []
for i in range(1, docker_instances + 1):
    token.append(os.environ.get(f'LICENSE_API_TOKEN_' + str(i)))

db_name = os.environ.get('POSTGRES_NAME')
db_port = os.environ.get('POSTGRES_PORT')
db_user = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')

redis_port          = 6380
jesse_listen_port   = 9000
jupyter_port        = 8800

environment = Environment(loader=FileSystemLoader("templates/"))
docker_tpl  = environment.get_template("docker-compose.yml")
jesse_tpl   = environment.get_template("jesse.yml")
redis_tpl   = environment.get_template("redis.yml")
env_tpl     = environment.get_template("env")

jesse_content = ""
redis_content = ""
database_content = "jesse_db_1"
for i in range(1, docker_instances + 1):
    jesse_content += jesse_tpl.render(id = i, listen_port = jesse_listen_port + i - 1, jupyter_port = jupyter_port + i - 1)
    redis_content += redis_tpl.render(id = i, export_port = redis_port + i - 1)
    if i > 1:
        database_content += ", jesse_db_" + str(i)
    instance = "instance-" + str(i) + "/";
    os.makedirs(instance, exist_ok=True)
    shutil.copy("templates/checkdb.py", instance + "checkdb.py")
    with open(instance + ".env", mode="w", encoding="utf-8") as message:
        env_content = env_tpl.render(database_name = "jesse_db_"+ str(i) ,token = token[i - 1], redis_host = "redis-"+ str(i))
        message.write(env_content)


docker_content = docker_tpl.render(jesse = jesse_content, redis = redis_content, databases = database_content)

os.makedirs("docker", exist_ok=True)
os.makedirs("docker/docker-postgresql-multiple-databases", exist_ok=True)
os.makedirs("docker/postgres-data", exist_ok=True)

create_db = "docker/docker-postgresql-multiple-databases/createdbs.sh"
shutil.copy("templates/createdbs.sh",create_db)

# Make the file executable
st = os.stat(create_db)
os.chmod(create_db, st.st_mode| stat.S_IEXEC)

with open("docker/docker-compose.yml", mode="w", encoding="utf-8") as message:
    message.write(docker_content)

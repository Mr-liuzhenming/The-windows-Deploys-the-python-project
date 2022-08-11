import os
import sys
import time


def get_cmd(cmd):
    res = os.popen(cmd)
    return res.read()


class Generate:
    def __init__(self, dockerfile_name="generate.dockerfile", image_name="docker_img"):
        self.dockerfile_name = dockerfile_name
        self.image_name = image_name

    def generate_dockerfile(self, work_dir="/usr/src/app", main_file="app.py"):
        # 首先生成dockerfile模板,python版本通过命令行获取
        python_version = sys.version.split(" ")[0]
        template = f"""
FROM python:{python_version}
WORKDIR {work_dir}
COPY requirements.txt {work_dir}
RUN pip install -i https://pypi.doubanio.com/simple/ -r requirements.txt
COPY . {work_dir}
CMD [ "python", "{work_dir}/{main_file}" ]
"""
        # 检查requirements.txt文件是否存在，不存在则调用命令生成生成
        if not os.path.exists("requirements.txt"):
            print("正在等待requirements.txt文件生成,请稍候....")
            os.system("pip install -i https://pypi.doubanio.com/simple/ pipreqs && pipreqs ./ --encoding=utf8 --force")
            while not os.path.exists("requirements.txt"):
                print("正在等待requirements.txt文件生成...")
                time.sleep(2)

        # 确定requirements文件生成后，将dockerfile写入到本地
        with open(self.dockerfile_name, "w") as f:
            f.write(template)
        print(f"dockerfile生成成功，文件名称为{self.dockerfile_name}")
        return True

    def build_image(self):
        images = get_cmd(f"docker images")
        if self.image_name not in images:
            cmd = f"docker build -f {self.dockerfile_name} -t {self.image_name} ."
            print(cmd)
            os.system(cmd)
            return self.image_name in images
        return False

    def run_container(self, container_name, local_port=5001, container_port=5000):
        cmd = f"docker run -p {local_port}:{container_port} --name {container_name} {self.image_name}"
        # cmd = f"docker run {self.image_name}"
        print(cmd)
        os.system(cmd)


if __name__ == '__main__':
    generate = Generate(dockerfile_name="generate_dockerfile.dockerfile", image_name="epidemic")
    generate.generate_dockerfile()
    generate.build_image()
    generate.run_container(container_name="epidemic_container", local_port=5001, container_port=5000)

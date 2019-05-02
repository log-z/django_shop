# django_shop

基于Django开发的网上商城（逐步进行中...）


## 开始使用

1. 安装依赖库。必备的第三方库列在 ``/requirements.txt`` 清单文件中，pip 用户通过以下指令可自动化安装所有依赖库。
   
   ```
   $ pip install -r requirements.txt
   ```
     
2. 数据库迁移（初次使用可跳过）。如果已经存在旧版本项目，那么请迁移数据库到最新版本。通过以下指令即可执行迁移。

   ```
   $ cd project_path
   $ python manage.py migrate
   ```

3. 运行 Django 服务。（商城首页地址类似于 ``http://127.0.0.1:8000/shop`` ）

   ```
   $ cd project_path
   $ python manage.py runserver
   ```


## 功能实现

   * [x] 浏览商品列表（测试通过）
   * [x] 查看商品详情（测试通过）
   * [x] 查询商品（测试通过）
   * [x] 用户注册（未测试）
   * [ ] 用户登陆
   * [ ] 查看用户信息
   * [ ] 修改用户信息
   * [ ] ……
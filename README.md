# django_shop

基于Django开发的网上商城（逐步进行中...）


## 开始使用

1. 安装依赖库。必备的第三方库已列在 ``requirements.txt`` 清单文件中，pip 用户通过以下指令可自动化安装所有依赖库。
   
   ```
   $ pip install -r requirements.txt
   ```
     
2. 数据库迁移。初次使用前，或者更新代码后，都请务必迁移数据库到最新版本。通过以下指令即可完成迁移。

   ```
   $ python manage.py migrate
   ```

3. 运行 Django 服务。（商城首页地址默认是 ``http://127.0.0.1:8000/shop`` ）

   ```
   $ python manage.py runserver
   ```

## 测试与维护

-  执行单元测试。

   ```
   $ python django test shop
   ```
   
-  清理数据库中已过期的 Session 记录。Django 不会主动清理已过期的 Session 数据，所以请你通过配置计划任务的方式定时执行以下命令，清理掉不必要的数据。

   ```
   $ python manage.py clearsessions
   ```


## 存在问题

1. 商品管理尚未实现，商品的创建、修改和删除暂时需要通过管理页面操作，管理页面地址默认是 ``http://127.0.0.1:8000/admin`` 。管理员账号的创建请参考[官方文档](https://docs.djangoproject.com/zh-hans/2.1/intro/tutorial02/#introducing-the-django-admin)。


## TODO LIST

   * [x] 浏览商品
      * [x] 商品列表 [测试通过]
      * [x] 商品详情 [测试通过]
      * [x] 查询商品 [测试通过]
   * [x] 用户支持
      * [x] 用户注册 [测试通过]
      * [x] 用户登陆 [测试通过]
      * [x] 用户退出 [测试通过]
   * [ ] 个人中心
      * [ ] 个人信息管理 [进行中]
      * [ ] 收货地址管理
      * [ ] 申请成为商家
   * [ ] 商家中心
      * [ ] 店铺信息管理
      * [ ] 商品管理
         * [ ] 商品信息
         * [ ] 上架/下架
         * [ ] 订单管理
   * [ ] 管理员中心
      * [ ] 用户管理
      * [ ] 审批管理
   * [ ] 用户消费
      * [ ] 直接购买
      * [ ] 购物车
   * [ ] ……

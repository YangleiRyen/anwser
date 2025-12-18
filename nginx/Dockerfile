# 使用官方Nginx镜像
FROM nginx:1.25-alpine

# 维护者信息
LABEL maintainer="Your Name <your.email@example.com>"

# 删除默认的nginx配置文件
RUN rm /etc/nginx/conf.d/default.conf

# 复制自定义的nginx配置文件
COPY conf.d/ /etc/nginx/conf.d/

# 复制主nginx配置文件（如果需要）
# COPY nginx.conf /etc/nginx/nginx.conf

# 暴露80端口
EXPOSE 80

# 启动nginx服务
CMD ["nginx", "-g", "daemon off;"]

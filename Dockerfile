# 基础镜像必须钉版本，不能追 latest：本仓库的 cps/ 是 fork 的旧代码，COPY 进
# 基础镜像后依赖全用基础镜像里的。latest 升级会带来新版 Python 库（2026-08
# 实测 flask-limiter 移除 auto_check 参数，容器直接起不来），而 requirements.txt
# 并不参与 build。想升基础镜像时，连同 cps/ 代码一起对齐上游版本再升。
FROM lscr.io/linuxserver/calibre-web:0.6.26-ls385

WORKDIR /app/calibre-web

COPY . /app/calibre-web

RUN chown -R abc:abc /app/calibre-web

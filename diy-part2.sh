#!/bin/bash
#
# Copyright (c) 2019-2020 P3TERX <https://p3terx.com>
#
# This is free software, licensed under the MIT License.
# See /LICENSE for more information.
#
# https://github.com/P3TERX/Actions-OpenWrt
# File name: diy-part2.sh
# Description: OpenWrt DIY script part 2 (After Update feeds)
#

# Modify default IP
#sed -i 's/192.168.1.1/192.168.50.5/g' package/base-files/files/bin/config_generate
#修改默认的IP
#sed -i 's/192.168.1.1/10.10.10.1/g' openwrt/package/base-files/files/bin/config_generate

#files目录权限
#chmod -R 755 files

#修改主机名
#sed -i '/uci commit system/i\uci set system.@system[0].hostname='Soft_Routes'' openwrt/package/lean/default-settings/files/zzz-default-settings

#设置密码为空
#sed -i 's@.*CYXluq4wUazHjmCDBCqXF*@#&@g' openwrt/package/lean/default-settings/files/zzz-default-settings

#版本号里显示一个自己的名字
#sed -i "s/OpenWrt /OpenWrt build $(TZ=UTC-8 date "+%Y.%m.%d") @ OpenWrt /g" package/lean/default-settings/files/zzz-default-settings
#sed -i "s/OpenWrt /Allok build $(TZ=UTC-8 date "+%Y.%m.%d") @ OpenWrt /g" package/lean/default-settings/files/zzz-default-settings

#修改插件名字
#sed -i 's/"Turbo ACC 网络加速"/"网络加速"/g' openwrt/package/lean/luci-app-sfe/po/zh-cn/sfe.po
        
#修改上游DNS
#sed -i "2i # network config" openwrt/package/lean/default-settings/files/zzz-default-settings
#sed -i "3i uci set network.lan.dns='114.114.114.114'"  openwrt/package/lean/default-settings/files/zzz-default-settings

# Mod zzz-default-settings（版本后显示编译日期）
pushd package/lean/default-settings/files
sed -i '/http/d' zzz-default-settings
export orig_version="$(cat "zzz-default-settings" | grep DISTRIB_REVISION= | awk -F "'" '{print $2}')"
sed -i "s/${orig_version}/${orig_version} ($(date +"%Y-%m-%d"))/g" zzz-default-settings
popd

# Add luci-theme-argon
#git clone --depth=1 -b 18.06 https://github.com/jerrykuku/luci-theme-argon
#git clone --depth=1 https://github.com/jerrykuku/luci-app-argon-config
#rm -rf ../lean/luci-theme-argon
# 把bootstrap替换成argon为源码必选主题（可自行修改您要的,主题名称必须对,比如下面代码的[argon],源码内必须有该主题,要不然编译失败）
sed -i "s/bootstrap/argon/ig" feeds/luci/collections/luci/Makefile

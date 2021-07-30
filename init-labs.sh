#!/bin/sh
git clone git@github.com:alexeykr65/net-labs-ansible.git $1
cd $1
[ ! -d "net-stack" ] && mkdir net-stack
git clone git@github.com:alexeykr65/net-labs.git
echo "create new files "
for f in net-labs/*.yaml; do
    echo $f
    gen-heatv3.py -l $f
done
cat << END >oslabs.yml
---
wan: wan0
lab: $1
END




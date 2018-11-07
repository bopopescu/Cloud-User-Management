    def instance_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi instance_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'instance_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def instance_delete(self, context, container, force):
        LOG.debug('rpcapi instance_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'instance_delete',
                          container=container, force=force)

    #@check_container_host
    def instance_show(self, context, container):
        return self._call("", 'instance_show',
                          container=container)

    #@check_container_host
    def instance_update(self, context, container, patch):
        LOG.debug('instance_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'instance_update',
                          container=container, patch=patch)

    

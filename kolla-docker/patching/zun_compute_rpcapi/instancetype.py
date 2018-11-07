    def instancetype_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi instancetype_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'instancetype_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def instancetype_delete(self, context, container, force):
        LOG.debug('rpcapi instancetype_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'instancetype_delete',
                          container=container, force=force)

    #@check_container_host
    def instancetype_show(self, context, container):
        return self._call("", 'instancetype_show',
                          container=container)

    #@check_container_host
    def instancetype_update(self, context, container, patch):
        LOG.debug('instancetype_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'instancetype_update',
                          container=container, patch=patch)

    

    def computerate_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi computerate_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'computerate_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def computerate_delete(self, context, container, force):
        LOG.debug('rpcapi computerate_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'computerate_delete',
                          container=container, force=force)

    #@check_container_host
    def computerate_show(self, context, container):
        return self._call("", 'computerate_show',
                          container=container)

    #@check_container_host
    def computerate_update(self, context, container, patch):
        LOG.debug('computerate_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'computerate_update',
                          container=container, patch=patch)

    

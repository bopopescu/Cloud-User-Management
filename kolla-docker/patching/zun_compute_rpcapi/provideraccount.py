    def provideraccount_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi provideraccount_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'provideraccount_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def provideraccount_delete(self, context, container, force):
        LOG.debug('rpcapi provideraccount_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'provideraccount_delete',
                          container=container, force=force)

    #@check_container_host
    def provideraccount_show(self, context, container):
        return self._call("", 'provideraccount_show',
                          container=container)

    #@check_container_host
    def provideraccount_update(self, context, container, patch):
        LOG.debug('provideraccount_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'provideraccount_update',
                          container=container, patch=patch)

    

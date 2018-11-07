    def providerregion_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi providerregion_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'providerregion_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def providerregion_delete(self, context, container, force):
        LOG.debug('rpcapi providerregion_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'providerregion_delete',
                          container=container, force=force)

    #@check_container_host
    def providerregion_show(self, context, container):
        return self._call("", 'providerregion_show',
                          container=container)

    #@check_container_host
    def providerregion_update(self, context, container, patch):
        LOG.debug('providerregion_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'providerregion_update',
                          container=container, patch=patch)

    

    def providervm_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi providervm_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'providervm_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def providervm_delete(self, context, container, force):
        LOG.debug('rpcapi providervm_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'providervm_delete',
                          container=container, force=force)

    #@check_container_host
    def providervm_show(self, context, container):
        return self._call("", 'providervm_show',
                          container=container)

    #@check_container_host
    def providervm_update(self, context, container, patch):
        LOG.debug('providervm_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'providervm_update',
                          container=container, patch=patch)

    

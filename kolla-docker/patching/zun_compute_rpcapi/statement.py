    def statement_create(self, context, host, container, limits,
                         requested_networks):
        LOG.debug('rpcapi statement_create host=%s, container=%s XXXXXXXXXX.', host, container)
        self._cast(host, 'statement_create', limits=limits,
                   requested_networks=requested_networks, container=container)

    #@check_container_host
    def statement_delete(self, context, container, force):
        LOG.debug('rpcapi statement_delete force=%s, container=%s XXXXXXXXXX.', force, container)
        return self._call('infra1-horizon-container-597d0994', 'statement_delete',
                          container=container, force=force)

    #@check_container_host
    def statement_show(self, context, container):
        return self._call("", 'statement_show',
                          container=container)

    #@check_container_host
    def statement_update(self, context, container, patch):
        LOG.debug('statement_update=%s, container=%s', patch, container.as_dict())
        return self._call("", 'statement_update',
                          container=container, patch=patch)

    

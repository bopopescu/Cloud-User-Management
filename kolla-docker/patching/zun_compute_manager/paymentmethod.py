    def _do_paymentmethod_create_base(self, context, container, requested_networks,
                                  limits=None, reraise=False):
        LOG.error("xxx _do_paymentmethod_create_base")
        container.task_state = consts.CONTAINER_CREATING
        container.save(context)
        try:
            self._update_task_state(context, container, None)
            return container
        except exception.DockerError as e:
            with excutils.save_and_reraise_exception(reraise=reraise):
                LOG.error("Error occurred while calling Docker create API: %s",
                          six.text_type(e))
                self._fail_container(context, container, six.text_type(e),
                                 unset_host=True)
            return
        except Exception as e:
            with excutils.save_and_reraise_exception(reraise=reraise):
                LOG.exception("Unexpected exception: %s",
                              six.text_type(e))
                self._fail_container(context, container, six.text_type(e),
                                     unset_host=True)
            return

    def _do_paymentmethod_create(self, context, container, requested_networks,
                             limits=None, reraise=False):
        LOG.debug('Creating container: %s', container.uuid)

        created_container = self._do_paymentmethod_create_base(context,
                                                           container,
                                                           requested_networks,
                                                           limits,
                                                           reraise)
        return created_container

    def paymentmethod_create(self, context, limits, requested_networks, container):
        self._do_paymentmethod_create(context, container, requested_networks,limits, False)


    @translate_exception
    def paymentmethod_delete(self, context, container, force):
        LOG.debug('Deleting paymentmethod: %s, context=%s, force=%s', container.uuid, context, force)
        self._update_task_state(context, container, consts.CONTAINER_DELETING)
        reraise = not force

        self._update_task_state(context, container, None)
        container.destroy(context)

        return container




    @translate_exception
    def paymentmethod_show(self, context, container):
        LOG.debug('Showing paymentmethod: %s', container.uuid)
        try:
            #container = self.driver.show(context, container)
            if container.obj_what_changed():
                container.save(context)
            return container
        except exception.DockerError as e:
            LOG.error("Error occurred while calling Docker show API: %s",
                      six.text_type(e))
            raise
        except Exception as e:
            LOG.exception("Unexpected exception: %s", six.text_type(e))
            raise




    @translate_exception
    def paymentmethod_update(self, context, container, patch):
        LOG.debug('Updating a paymentmethod: %s', container.uuid)
        # Update only the fields that have changed
        for field, patch_val in patch.items():
            if getattr(container, field) != patch_val:
                setattr(container, field, patch_val)

        try:
            #self.driver.update(context, container)
            container.save(context)
            return container
        except exception.DockerError as e:
            LOG.error("Error occurred while calling docker API: %s",
                      six.text_type(e))
            raise




    @periodic_task.periodic_task(run_immediately=True)
    def delete_unused_paymentmethods(self, context):
        """Delete container with status DELETED"""
        # NOTE(kiennt): Need to filter with both status (DELETED) and
        #               task_state (None). If task_state in
        #               [CONTAINER_DELETING, SANDBOX_DELETING] it may
        #               raise some errors when try to delete container.
        filters = {
            'status': consts.DELETED,
        }
        containers = objects.Paymentmethod.list(context,
                                            filters=filters)

        if containers:
            for container in containers:
                try:
                    msg = ('%(behavior)s deleting paymentmethod '
                           '%(container_name)s with status DELETED')
                    LOG.info(msg, {'behavior': 'Start',
                                   'container_name': container.name})
                    self.paymentmethod_delete(context, container, True)
                    LOG.info(msg, {'behavior': 'Complete',
                                   'container_name': container.name})
                except exception.DockerError:
                    return
                except Exception:
                    return

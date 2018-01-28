from celery.task import Task


class DeleteEmptyAttitudes(Task):
    significant_kwargs = []
    herd_avoidance_timeout = 0

    def run(self, sender, instance_id, **kwargs):
        instance = sender.objects.get(id=instance_id)
        attitude = False
        for code in instance.codes:
            attitude |= getattr(instance, code)

        if not attitude:
            instance.delete()

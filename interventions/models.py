from tasks.models import Intervention as TaskIntervention


class Intervention(TaskIntervention):
    """Domain-facing proxy; storage remains backward-compatible for now."""

    class Meta:
        proxy = True
        app_label = 'interventions'

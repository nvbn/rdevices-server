from django_extensions.db.fields import UUIDField


class ReUUIDField(UUIDField):
    """UUID field with fixed regeneration"""

    def create_uuid(self):
        """Create uuid as str"""
        return str(
            super(ReUUIDField, self).create_uuid(),
        )

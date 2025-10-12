from model_utils.models import UUIDModel, TimeStampedModel, SoftDeletableModel


class BaseModel(UUIDModel, TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True
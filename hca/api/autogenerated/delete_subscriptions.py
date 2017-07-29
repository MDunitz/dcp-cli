from ...added_command import AddedCommand

class DeleteSubscriptions(AddedCommand):
    """Class containing info to reach the get endpoint of files."""

    @classmethod
    def _get_base_url(cls):
        return "https://hca-dss.czi.technology/v1"

    @classmethod
    def get_command_name(cls):
        return "delete-subscriptions"

    @classmethod
    def _get_endpoint_info(cls):
        return {u'function_def_arglist': [(u'uuid', u'required'), (u'replica', u'required')], u'body_params': {}, u'positional': [{u'description': u'A RFC4122-compliant ID for the subscription.', u'format': None, u'pattern': u'[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}', u'required': True, u'argument': u'uuid', u'required_for': [u'/subscriptions/{uuid}'], u'type': u'string'}], u'seen': False, u'options': {u'replica': {u'hierarchy': [u'replica'], u'in': u'query', u'description': u'Replica to delete from. Can be one of aws, gcp, or azure.', u'required_for': [u'/subscriptions/{uuid}'], u'format': None, u'pattern': None, u'array': False, u'required': True, u'type': u'string', u'metavar': None}}, u'description': u'Delete a registered event subscription. The associated query will no longer trigger a callback\nif a matching document is added to the system.\n'}

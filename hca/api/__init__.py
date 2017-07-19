from .autogenerated.get_bundles import GetBundles
from .autogenerated.put_bundles import PutBundles
from .autogenerated.get_files import GetFiles
from .autogenerated.head_files import HeadFiles
from .autogenerated.put_files import PutFiles
from .autogenerated.get_search import GetSearch
from .autogenerated.post_search import PostSearch


def get_bundles(uuid=None, version=None, replica=None, ):
    """
    Returns a list of bundles matching given criteria.

    :param uuid: Bundle unique ID.
    :param replica: Replica to fetch from.
    :param version: Timestamp of bundle creation in RFC3339.
    """
    return GetBundles.run(uuid, replica, version)


def put_bundles(uuid, version=None, replica=None, creator_uid=None, files=None, ):
    """
    Create a new version of a bundle with a given UUID.  The list of file UUID+versions to be included must be
    provided.

    :param uuid: A RFC4122-compliant ID for the bundle.
    :param creator_uid: User ID who is creating this bundle.
    :param files: indexed: True iff this file should be indexed.
        name: Name of the file.
        uuid: A RFC4122-compliant ID for the file.
        version: Timestamp of file creation in RFC3339.
    :param replica: Replica to write to.
    :param version: Timestamp of bundle creation in RFC3339.
    """
    return PutBundles.run(uuid, creator_uid, files, replica, version)


def get_files(uuid=None, replica=None, version=None, ):
    """
    Returns a list of files matching given criteria.

    :param uuid: A RFC4122-compliant ID for the file.
    :param replica: Replica to fetch from.
    :param version: Timestamp of file creation in RFC3339.  If this is not provided, the latest version is returned.
    """
    return GetFiles.run(uuid, replica, version)


def head_files(uuid, version=None, ):
    """
    Given a file UUID, return the metadata for the latest version of that file.  If the version is provided, that
    version's metadata is returned instead.  The metadata is returned in the headers.

    :param uuid: A RFC4122-compliant ID for the file.
    :param version: Timestamp of file creation in RFC3339.  If this is not provided, the latest version is returned.
    """
    return HeadFiles.run(uuid, version)


def put_files(uuid, version=None, bundle_uuid=None, creator_uid=None, source_url=None, ):
    """
    Create a new version of a file with a given UUID.  The file content is passed in through a cloud URL.  The file
    on the cloud provider must have metadata set reflecting the file checksums and the file content type.

    The metadata fields required are:
    - hca-dss-content-type: content-type of the file
    - hca-dss-sha256: SHA-256 checksum of the file
    - hca-dss-sha1: SHA-1 checksum of the file
    - hca-dss-s3_etag: S3 ETAG checksum of the file.  See
    https://stackoverflow.com/questions/12186993/what-is-the-algorithm-to-compute-the-amazon-s3-etag-for-a-file-larger-than-5gb
    for the general algorithm for how checksum is calculated.  For files smaller than 64MB, this is the MD5 checksum
    of the file.  For files larger than 64MB but smaller than 640,000MB, we use 64MB chunks.  For files larger than
    640,000MB, we use a chunk size equal to the total file size divided by 10000, rounded up to the nearest MB.
    MB, in this section, refers to 1,048,576 bytes.  Note that 640,000MB is not the same as 640GB!
    - hca-dss-crc32c: CRC-32C checksum of the file

    :param uuid: A RFC4122-compliant ID for the bundle.
    :param bundle_uuid: A RFC4122-compliant ID for the bundle that contains this file.
    :param creator_uid: User ID who is creating this file.
    :param source_url: Cloud URL for source data.
    :param version: Timestamp of file creation in RFC3339.  If this is not provided, the latest version is returned.
    """
    return PutFiles.run(uuid, bundle_uuid, creator_uid, source_url, version)


def get_search(query=None, ):
    """
    Returns a list of bundles matching the given simple criteria

    :param query: Metadata query
    """
    return GetSearch.run(query)


def post_search():
    """
    Accepts Elasticsearch JSON query and returns matching bundle identifiers

    """
    return PostSearch.run()

import MySQLdb
import MySQLdb.cursors
import logger
from pod import podutils
import re

key_parse = podutils.podsettings()
DBHOST = key_parse.get('cmdb_master_host','global')
DBUSER = key_parse.get('cmdb_master_user','global')
DBPASSWD = key_parse.get('cmdb_master_pass','global')
DBPORT = int(key_parse.get('cmdb_master_port','global'))
DBNAME = key_parse.get('cmdb_master_dbname','global')

pod_name = 'UATCELL-MASTER-01'

def connect_mysql(host=DBHOST, usernm=DBUSER, passwd=DBPASSWD, name=DBNAME):

    logging.debug('connect_mysql: starting')
    # Open database connection
    try:
        dbh = MySQLdb.connect(
            host=host, user=usernm, passwd=passwd, db=name,
            cursorclass=MySQLdb.cursors.DictCursor)
    except Exception, err:
        logging.error('connect_mysql: exit because ...')
        logging.error(err)
        sys.exit(1)

    return dbh

def query_mysql(dbh, sql, param=None):
    """query to mysql with SQL statement and parameter.
    sql is a SQL statetment. param is var as tuple. paramstyle is 'format'
    see more details, http://www.python.org/dev/peps/pep-0249/#paramstyle

    """
    logging.debug('query_mysql: starting')
    # prepare a cursor object using cursor() method
    cursor = dbh.cursor()
    logging.info(sql)
    # execute SQL query using execute() method.
    try:
        cursor.execute(sql, param)
    except TypeError:
        # param = None,
        # TypeError: not all arguments converted during string formatting
        pass
    except Exception, err:
        logging.error('query_mysql: exit because ...')
        logging.error(err)
        logging.error('SQL: ' + sql)
        if 'Duplicate entry' in str(err) :
            raise err
        sys.exit(1)

    # Fetch a single row using fetchone() method.
    results = cursor.fetchall()
    cursor.close()
    if results:
        logging.debug('Value: {0:s}'.format(results))
    else:
        logging.error('Return rows of sql query is 0.')
        return None

    return results


def is_not_alive(hostname, timeout_seconds=30):
    netstatus = commands.getoutput("ping -c 1 -w %s %s" % (timeout_seconds, hostname))
    if (re.compile("0 received, 100% packet loss").search(netstatus)):
        return True
    elif (re.compile("ping: unknown host %s" % hostname).search(netstatus)):
        return True
    else:
        return False


my_logger = logger.init_file_logging(config._bmc_ap_exception_handlewideanglebmcLog, config.logfileSize, config.logfileMaxNum)
my_logger = logging.getLogger(__name__)

my_logger.info("getting list of active devices from current POD:==")
pod_sql = "select id from cmsdev_pod where pod_id = '%s' UNION select id from cmsdev_pod where parent_pod_id=(select id from cmsdev_pod where pod_id = '%s')"%(pod_name)

active_device_sql = "select device_id from cmsdev_device where pod_id in (%s) and active=1"

dbh = connect_mysql()
pod_id_record = query_mysql(dbh, pod_sql)
pod_id_record = join(',',pod_id_record)
active_device_sql = active_device_sql%(pod_id_record)
device_list = query_mysql(dbh, active_device_sql)


#Find no of threads
t_no = len(device_list)%20


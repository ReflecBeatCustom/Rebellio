import hashlib

def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def generate_standard_result(result):
    """
    生成标准返回格式
    """
    standard_result = {}
    standard_result['total'] = len(result)
    standard_result['data'] = result
    return standard_result
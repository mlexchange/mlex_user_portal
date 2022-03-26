from neo4j import GraphDatabase, basic_auth

class userAPI:

    def __init__(self, url, auth):
        self.url     = url
        self.auth    = auth
        self.driver  = GraphDatabase.driver(url, auth=basic_auth(self.auth[0], self.auth[1]))
        self.session = self.driver.session()
        self.role_count = {'Admin': 0, 'Sub-Admin': 0, 'Developer': 0, 'General-User': 0}

        ### For developing purpose (i.e. need to delete this when is stable)
        for r in self.role_count.keys():
            status = self.delete_role(r)

        # Initiate all roles
        for r in self.role_count.keys():
            status = self.create_role(r)

        # Initiate action: full access, read, write
        self.create_action()

        ### For developing purpose
        ### Create default users for testing
        self.delete_default_users()
        self.add_default_users()

        ### For developing purpose
        ### add_content_asset
        self.add_content_asset('Model01', 'trained_model', 'HKrish00003')

    
    def create_role(self, role):
        parameters = {'role': role}
        cquery = '''
        create (r:Role:Attribute {name:$role})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_role(self, role):
        if role not in self.role_count:
            self.role_count[role] = 0
        status = self.create_role(role)
        return status


    def delete_role(self, role):
        parameters = {'role': role}
        cquery = '''
        match (r:Role {name:$role})
        detach delete r
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status
       

    def add_user(self, fname, lname, email, role='General-User'):
        if role not in self.role_count:
            msg = 'The assigned role is not in the system.\nPlease add the intended role to the system.'
            return ValueError(msg)
        cquery = '''
        match (u:User) return u
        '''
        dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
        temp_id = str(fname[0] + lname + str(dbindx).zfill(5))
        
        parameters = {'temp_id': temp_id, 'fname': fname, 'lname': lname, 'email': email, 'role': role}
        cquery = '''
        match (r:Role {name:$role})
        create (n:Subject:User:Primitive {uid: $temp_id, fname:$fname, lname:$lname, email:$email})-[:has_attr]->(r)
        '''
        status = self.session.run(cquery, parameters=parameters)
        # Perhaps, we want to create new user without assigning role?
        # If this is the case, why don't General-User be the default?
        return status


    def create_user_profile(self):
        # I'm thinking that user node should only contains uid.
        # Meanwhile, we can create another node for the user that contains his/her profile. This node is called profile node.
        # Profile will include, but not limited to, first name, last name, email, institution, etc.
        status = None
        return status

    
    def assign_user_role(self, uid, role, prev_role=None):
        # If the role is already general-user, do nothing
        if role == 'General-User':
            return None

        # If one user is assigned to one role, then:
        # Delete relationship with the previous role
        if prev_role:
            self.delete_user_role(uid, prev_role)

        parameters = {'uid': uid, 'rname': role}
        cquery = '''
        match (u:User {uid:$uid}), (r:Role {name:$role})
        merge (u)-[:has_attr]->(r)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_user_role(uid, role):
        parameters = {'uid': uid, 'role': role}
        cquery = '''
        match (u:User {uid: $uid})-[rel:has_attr]->(r:Role {name:$role})
        delete rel
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    
    def delete_user(self, uid):
        # How do one get the uid?
        parameters = {'uid': uid}
        cquery = '''
        match (u:User {uid:$uid})
        detach delete (u)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_action(self):
        cquery = '''
        merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
        '''
        status = self.session.run(cquery)
        return status

    
    def add_default_users(self):
        self.add_user('Howard', 'Yanxon', 'hg.yanxon@gmail.com', 'Developer')
        self.add_user('Elizabeth', 'Holman', 'liz@gmail.com', 'Developer')
        self.add_user('Hari', 'Krish', 'krish@gmail.com', 'Admin')
        self.add_user('John', 'Smith', 'smithj123@gmail.com', 'General-User')


    def delete_default_users(self):
        uids = ['HYanxon00001', 'EHolman00002', 'HKrish00003', 'JSmith00004']
        for uid in uids:
            status = self.delete_user(uid)
        return status

    
    #def add_compute_location(self, cname, clocation):
    #    parameters = {'cname': cname, 'clocation':clocation}
    #    cquery = '''
    #    create (n:compute:Object:Location {cname: $cname, clocation:$clocation})
    #    '''
    #    status = self.session.run(cquery, parameters=parameters)
    #    return status


    #def delete_compute_location(self, cname, clocation):
    #    parameters = {'cname': cname, 'clocation':clocation}
    #    cquery = '''
    #    match (c:compute:Object:Location {cname:$cname, clocation:$clocation})
    #    detach delete (c)
    #    '''
    #    status = self.session.run(cquery, parameters=parameters)
    #    return status

    #
    #def add_content_asset(self, aname, atype, owner):
    #    auid = owner + '_'
    #    owner_belonging = owner + '\'s' + atype

    #    parameters = {'aname': owner_belonging, 'atype': atype, 'auid': auid, 'owner': owner}
    #    cquery = '''
    #    create (AssetOne:content:Group:Attribute {aname: $aname, atype: $atype, a_uid: toString(($auid)+toString(timestamp())), owner: $owner})
    #    return AssetOne.a_uid
    #    '''
    #    a_uid = self.session.run(cquery, parameters=parameters)
    #    print(a_uid.__dict__)
    #    print(a_uid.a_uid)
    #    import sys; sys.exit()
    #    print(a_uid)
    #
    #    parameters = {'a_uid': a_uid}
    #    cquery = '''
    #    match (u:User {uid: $owner})
    #    match (c:content {a_uid: $a_uid})
    #    merge (u)-[:owner_of]->(c)<-[:has_attr]-(rec:Data:Object:Primitive {a_uid: $a_uid})
    #    '''
    #    status = self.session.run(cquery, parameters)
    #    return status
        

    def delete_content_asset(self):
        return

    def delete_user_asset(self):
        return

    def add_user_team(self):
        return

    def create_user_team(self):
        return

    def delete_user_team(self):
        return

    def remove_user_team(self):
        return


if __name__ == '__main__':
    api = userAPI(url="bolt://100.27.25.207:7687",
                  auth=("neo4j", "articles-researchers-accordance"))
    api.driver.close()

    ### Need to verify if each of the methods in the userAPI class are working

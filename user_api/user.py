from neo4j import GraphDatabase, basic_auth

class userAPI:

    def __init__(self, url, auth):
        self.url     = url
        self.auth    = auth
        self.driver  = GraphDatabase.driver(url, auth=basic_auth(self.auth[0], self.auth[1]))
        self.session = self.driver.session()
        self.role_count = {'Admin': 0, 'Developer': 0, 'MLE-User': 0, 'General-User': 0}

        ### For developing purpose (i.e. need to delete this when is stable)
        for r in self.role_count.keys():
            status = self.delete_role(r)

        # Initiate all roles
        for r in self.role_count.keys():
            status = self.create_role(r)
        
        ### For developing purpose. Delete MLExchange_Profile
        self.delete_MLExchange_profile()

        # Create MLExchange Profile
        self.create_MLExchange_profile()

        # Initiate action: full access, read, write
        self.create_action()

        ### For developing purpose
        ### Create default users for testing
        self.delete_default_users()
        self.add_default_users()

        ### For developing purpose
        ### Add compute location
        self.delete_compute_resource(cuid='c_MLSandbox00001')
        self.add_compute_resource(name='MLSandbox', location='Lawrence Berkeley National Laboratory', profile=None)

        ### For developing purpose
        ### Add Team
        self.remove_team('MLExchange_Team')
        self.add_team('MLExchange_Team')
        self.assign_user_team(uid='u_HKrish00003', team_name='MLExchange_Team')
        #self.remove_user_team(uid='u_HKrish00003', team_name='MLExchange_Team')

        ### For developing purpose
        ### Add a test policy
        #self.test_policy1()
        #self.test_policy2()
        
        ### For developing purpose
        ### add_content_asset
        #self.add_content_asset('Model01', 'trained_model', 'HKrish00003')
                

    def test_policy1(self):
        ''' Admin have full access of profiles. '''
        cquery = '''
        /// Policy 1 - Admin has full access of profiles 
        match (admin:Role {name: 'Admin'})
        match (mp:MasterProfile {name: "MLExchange Profile"})
        match (act:Attribute {name:"Full Access"})
        create (pol:Policy {name: 'Policy1', decision: 'Permit'})
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:OBJ_CON]-(mp)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status


    def test_policy2(self):
        status = None
        return status


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
        ''' A function to add user node. Every user is assigned as General-User after sign-up. '''
        
        if role not in self.role_count:
            msg = 'The assigned role is not in the system.\nPlease add the intended role to the system.'
            raise ValueError(msg)
        cquery = '''
        match (u:User) return u
        '''
        dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
        temp_id = 'u_' + str(fname[0] + lname + str(dbindx).zfill(5))
        
        profile_name = fname+'\'s Profile'
        parameters = {'temp_id': temp_id, 'fname': fname, 'lname': lname, 'email': email, 'role': role, 'profile_name': profile_name}
        
        cquery = '''
        match (r:Role {name:$role})
        match (ap:MasterProfile {name: "MLExchange Profile"})
        merge (n:Subject:User:Primitive {uid: $temp_id, fname:$fname, lname:$lname})-[:has_attr]->(r)
        // Create user's profile
        merge (n)-[:owner_of]->(p:UserProfile:Object 
        {name: $profile_name, uid: $temp_id, fname: $fname, lname: $lname, email: $email})-[:has_attr]->(ap)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status

    
    def create_MLExchange_profile(self, name='MLExchange Profile'):
        parameters = {'name': name}
        cquery = '''
        create (ap:MasterProfile:Attribute {name: $name})
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_MLExchange_profile(self, name='MLExchange Profile'):
        parameters = {'name': name}
        cquery = '''
        match (ap:MasterProfile {name: $name})
        detach delete ap
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def create_user_profile(self):
        # I'm thinking that user node should only contains uid.
        # Meanwhile, we can create another node for the user that contains his/her profile. This node is called profile node.
        # Profile will include, but not limited to, first name, last name, email, institution, etc.
        # I wonder if we need so make this separate from add_user because currently this function is included in add_user
        status = None
        return status

    
    def assign_user_role(self, uid, role, prev_role=None):
        ''' This method is to assign a user to a role. '''
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
        # This function should not need role as an argument.
        # Neo4j should know the role that is attached to the user.
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
        match (u:User {uid: $uid})
        match (p:UserProfile {uid: $uid})
        detach delete (u)
        detach delete (p)
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
        uids = ['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']
        for uid in uids:
            status = self.delete_user(uid)
        return status

    
    def add_compute_resource(self, name, location, profile=None):
        """
        We need to work on the profile argument. Essentially, profile contain ngpu, ncpu, etc. Then,
        we need to pass this information to the computing resource profile.
        """
        cquery = '''
        match (cr:ComputeResource) return cr
        '''
        dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
        cuid = 'c_' + name + str(dbindx).zfill(5)
        profile_name = name + '\'s Profile'

        parameters = {'name': name, 'location': location, 'cuid': cuid, 'profile_name': profile_name, 'profile': 'None'}
        cquery = '''
        match (ap:MasterProfile {name: "MLExchange Profile"})
        create (cr:ComputeResource:Object {name: $name, cuid: $cuid})
        merge (cr)-[:owner_of]->(cp:ComputeResourceProfile:Object {cuid: $cuid, profile_name: $profile_name, location: $location, profile: $profile})-[:has_attr]->(ap)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def delete_compute_resource(self, cuid):
        parameters = {'cuid': cuid}
        cquery = '''
        match (c:ComputeResource {cuid: $cuid})
        match (cp:ComputeResourceProfile {cuid: $cuid})
        detach delete (c)
        detach delete (cp)
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


    def add_team(self, name):
        cquery = '''
        match (t:Team {name: $name})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters={'name': name})
        is_present = False
        for s in status: is_present = s['is_present']
        
        if is_present:
            msg = 'The team name is already existed.'
            raise ValueError(msg)

        cquery = '''
        create (t:Team:Attribute {name: $name})
        '''
        status = self.session.run(cquery, parameters={'name': name})
        return status


    def remove_team(self, name):
        cquery = '''
        match (t:Team {name: $name})
        return exists(t.name) as is_present
        '''
        status = self.session.run(cquery, parameters={'name': name})
        is_present = False
        for s in status: is_present = s['is_present']
        
        if not is_present:
            msg = 'The team name doesn\'t exist.'
            raise ValueError(msg)

        cquery = '''
        match (t:Team {name: $name})
        detach delete t
        '''
        status = self.session.run(cquery, parameters={'name': name})
        return status


    def assign_user_team(self, uid, team_name):
        ''' This method is to assign a user to a team. '''
        # When check if the relationship exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uid': uid, 'name': team_name}
        cquery = '''
        match (u:User {uid: $uid}), (t:Team {name: $name})
        return exists((u)-[:has_attr]-(t)) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = status.single()[0]
        #print(is_present)

        if not is_present:
            cquery = '''
            match (u:User {uid: $uid})
            match (t:Team {name: $name})
            merge (u)-[:has_attr]->(t)
            '''
            status = self.session.run(cquery, parameters=parameters)
        return status


    def remove_user_team(self, uid, team_name):
        ''' This method is to remove a user from a team. '''
        # When check if the relationship exist, it always return False
        # If relationship is there it will break the relationship
        parameters = {'uid': uid, 'name': team_name}
        cquery = '''
        match (u:User {uid: $uid}), (t:Team {name: $name})
        return exists((u)-[:has_attr]-(t)) as is_present
        '''
        status = self.session.run(cquery, parameters=parameters)
        is_present = status.single()[0]
        #print(is_present)

        parameters = {'uid': uid, 'name': team_name}
        cquery = '''
        match (u:User {uid: $uid})-[r:has_attr]->(t:Team {name: $name})
        delete r
        '''
        status = self.session.run(cquery, parameters=parameters)
        return status


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


if __name__ == '__main__':
    api = userAPI(url="bolt://54.173.171.182:7687",
                  auth=("neo4j", "consolidation-taxis-icing"))
    api.driver.close()

    ### Need to verify if each of the methods in the userAPI class are working

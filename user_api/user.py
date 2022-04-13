from readline import get_current_history_length
#from typing_extensions import Self
from unittest import result

from numpy import column_stack
from neo4j import GraphDatabase, basic_auth

class userAPI:

    def __init__(self, url, auth):
        self.url     = url
        self.auth    = auth
        self.driver  = GraphDatabase.driver(url, auth=basic_auth(self.auth[0], self.auth[1]))
        self.session = self.driver.session()

    ### ROLES ###
    def create_role(self, role):
        """ Create a role node. """
        parameters = {'role': role}
        cquery = '''
        CALL {
            MATCH (r:Role {name:$role})
            RETURN count(r) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts > 0,
            'RETURN toInteger(0) AS result',
            'MERGE (r:Role:Attribute {name:role}) RETURN toInteger(1) AS result',
            {counts:counts, role:$role}) YIELD value
        RETURN value.result as results        
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('results') > 0:
            status = print("New " + str(role) + " role was created!")
        else:
            status = print("[WARNING] New role '" + str(role) + "' was not created. Role already exists.")
        return status

    def delete_role(self, role):
        """ Delete a role node. """
        parameters = {'role': role}
        cquery = '''
        CALL {
            MATCH (r:Role {name:$role})
            DETACH DELETE r
            RETURN r
        }
        WITH MATCH (r:Role {name:$role})
        RETURN toInteger(counts(r)) AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data().get('result')
        if result == 0:
            status = print("The " + str(role) + " was removed from the database.")
        else:
            status = print("[WARNING] The " + str(role) + " still exists in the database.")
        return status

    def add_user_to_role(self, uuid, role):
        """ Assigns a user to a role. """
        parameters = {'uuid': uuid, 'role': role}
        cquery = '''
        MATCH (r:Role {name:$role})
        CALL {
            MATCH (u:user {uuid:$uuid})-[rel:has_attr]->(role:Role:Attribute)
            DELETE rel
            RETURN u
        }
        WITH u, r 
        MERGE (u)-[rel:has_attr]->(r)
        RETURN toInteger(count(rel)) AS result
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('result') > 0:
            status = print("User " + str(uuid) + " now has the " + str(role) + " role.")
        else:
            status = print("[WARNING] User " + str(uuid) + " role was not updated.")
        return status

    def remove_user_from_role(self, uuid, role):
        """ Removes a role of a user and sets user role to general user. """
        parameters = {'uuid': uuid, 'role': role}
        cquery = '''
        MATCH (u:user {uuid: $uuid})-[rel:has_attr]->(r:Role {name:$role})
        DELETE rel
        WITH MATCH (u), (role:Role {name:'General User'})
        MERGE (u)-[:has_attr]->(role)
        RETURN u.uuid
        '''
        user_id = self.session.run(cquery, parameters=parameters)
        status = print("User " + str(user_id) + " has been removed from the " + str(role) + " and is now a General User.")
        return status

    ### USERS ###
    def create_user(self, fname, lname, email, orcid):
        """ A function to add user node. Every user is assigned as General User after sign-up. """
        test_query = '''
        MATCH (up:UserProfile {fname:$fname, lname:$lname, email:$email, orcid:$orcid})
        RETURN count(up) as counts
        '''
        counts = self.session.run(test_query, parameters={'fname':fname, 'lname':lname, 'email':email, 'orcid':orcid}).data()
        if counts[0].get('counts') > 0:
            status = print('User already exists. Have user ask admin for support.')
        else:
            cquery = '''
            match (u:user) return u
            '''
            dbindx = len([dict(_) for _ in self.session.run(cquery)]) + 1
            temp_id = 'u_' + str(fname[0] + lname + str(dbindx).zfill(5))
            
            parameters = {'temp_id': temp_id, 'fname': fname, 'lname': lname, 'email': email, 'orcid': orcid, 'role': 'General User'}
            cquery = '''
            MATCH (r:Role {name:$role})
            MERGE (up:UserProfile:Object 
            {fname: $fname, lname: $lname, email: $email, orcid: $orcid, uuid: $temp_id, active:True})<-[:owner_of]-(u:Subject:user:Primitive {uuid: $temp_id})-[:has_attr]->(r)
            SET u.active = True
            RETURN u.uuid AS userid
            '''
            user_id = self.session.run(cquery, parameters=parameters).data()
            if user_id:
                status = print("Account with user_id " + str(user_id[0].get('userid')) + " has been created!")
            else:
                status = print("[WARNING] An error occurred during user creation.")
        return status
    
    def archive_user(self, uuid):
        ''' Remove user from active user database and archive the uuid with its relationships to its owned assets. '''
        parameters = {'uuid': uuid}
        cquery = '''
        CALL {
            MATCH (up:UserProfile {uuid: $uuid})-[rel:has_attr]->()
            SET up.active = False
            RETURN rel AS rels
            UNION ALL
            MATCH (u:user {uuid: $uuid})-[rel:has_attr]->()
            SET u.active = False
            RETURN rel AS rels
        }
        WITH count(rels) AS counts, rels
        CALL apoc.do.when(counts = 0,
            'RETURN toInteger(1) AS result',
            'DELETE rels RETURN toInteger(0) AS result',
            {counts:counts, rels:rels}) YIELD value
        RETURN value.result AS activity
        '''
        activity = self.session.run(cquery, parameters=parameters).data()
        if activity is True:
            status = print("[WARNING] User " + str(uuid) + " is still active.")
        else:
            status = print("Account of " + str(uuid) + " has been set to inactive.")
        return status
    
    ### COMPUTE LOCATIONS ###
    def create_compute(self, name:str, hostname:str):
        """
        Create a compute location node. Name and location must uniquely define compute.
        """
        parameters = {'name': name, 'hostname': hostname}
        cquery = '''
        CALL {
            MATCH (cl:Compute {name:$name, hostname:$hostname})
            RETURN count(cl) AS counts
            }
        WITH counts, $name AS cl_name, $hostname AS cl_hostname
        CALL apoc.do.when(counts > 0,
            'RETURN toInteger(0) AS result',
            'CREATE (comp:Compute:Object {name:cl_name, hostname:cl_hostname}) RETURN toInteger(1) AS result',
            {counts:counts, cl_name:cl_name, cl_hostname:cl_hostname}) YIELD value
        RETURN value.result as result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] Compute location was not created. Please choose a different name and/or location to successfully create.") 
        else:
            status = print("Compute location has been created!")
        return status

    def delete_compute(self, name:str, hostname:str):
        """
        Deletes a compute location node and confirms the action. For admins only.
        """
        parameters = {'name': name, 'hostname':hostname}
        cquery = '''
        CALL {
            MATCH (cl:Compute {name:$name, hostname:$hostname})
            DETACH DELETE (cl)
            }
        MATCH (cl:Compute {name:$name, hostname:$hostname})
        RETURN count(cl) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("[WARNING] Compute location either was not removed or a duplicate exists.")
        else:
            status = print("Compute location with hostname " + str(hostname) + " either has been deleted or does not exist.")
        return status
    
    def add_user_to_compute(self, uuid:str, cname:str, chostname:str):
        ''' Assigns a user to a compute location. '''
        parameters = {'uuid': uuid, 'cname': cname, 'chostname':chostname}
        cquery = '''
        MATCH (u:user {uuid:$uuid}), (cl:Compute {name:$cname, hostname:$chostname})
        MERGE (u)-[relat:user_of]->(cl)
        RETURN count(relat) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("User " + str(uuid) + " now has access to compute location " + str(chostname) + ".")
        else:
            status = print("[WARNING] User " + str(uuid) + " access to compute location " +str(chostname) + " was not updated.")
        return status

    def remove_user_from_compute(self, uuid:str, cname:str, chostname:str):
        ''' Removes a user from compute location. '''
        parameters = {'uuid': uuid, 'cname': cname, 'chostname':chostname}
        cquery = '''
        MATCH (u:user {uuid:$uuid})-[rel:user_of]->(cl:Compute {name:$cname, hostname:$chostname})
        WITH rel, count(rel) as counts
        CALL apoc.do.when(counts > 0,
            'DELETE rel RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {rel:rel, counts:counts}) YIELD value
        RETURN value.result AS result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User " + str(uuid) + " access to compute hostname " +str(chostname) + " was not updated.")
        else:
            status = print("User " + str(uuid) + " has been removed from access to compute hostname " + str(chostname) + ".")
        return status
    
    ### TEAMS ###
    def create_team(self, name:str, owner:str):
        """ Create a team. Owner and admin access. """
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        CALL {
            MATCH (t:Team {name: $name, owner: $owner})
            RETURN count(t) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts = 0,
            'MATCH (u:user {uuid:$owner}) MERGE (u)-[:owner_of]->(n:Team:Attribute:Group {name: $name, owner: $owner}) RETURN toInteger(1) AS result',
            'RETURN toInteger(0) as result',
            {owner:$owner, name:$name}) YIELD value
        RETURN value.result AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if result == 0:
            status = print('[WARNING] User has already created a team with this name. Please use a different name.')
        else:
            status = print("Team " + str(name) + " has been successfully created.")
        return status

    def delete_team(self, name:str, owner:str):
        """ Delete team. Only owner or admin access. """
        parameters={'name':name, 'owner':owner} 
        cquery = '''
        CALL {
            MATCH (t:Team {name:$name, owner:$owner})
            RETURN count(t) AS counts
        }
        WITH counts
        CALL apoc.do.when(counts = 0,
            'RETURN toInteger(0) as result',
            'MATCH (t:Team {name:$name, owner:$owner}) DETACH DELETE t RETURN toInteger(1) AS result',
            {owner:$owner, name:$name}) YIELD value
        RETURN value.result AS result
        '''
        result = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if result == 0:
            status = print("[WARNING] User did not create a team called " + str(name) + ". Please use a different name.")
        else:
            status = print("Team " + str(name) + " was deleted from the database.")
        return status


    def add_user_to_team(self, uuid:str, tname:str, towner:str):
        """ Assign a user to a team. Restricted to admins and team owner."""
        parameters = {'uuid': uuid, 'tname': tname, 'towner':towner}
        cquery = '''
        MATCH (u:user {uuid:$uuid}), (t:Team {name:$tname, owner:$towner})
        MERGE (u)-[relat:has_attr]->(t)
        RETURN count(relat) as counts
        '''
        counts = self.session.run(cquery, parameters=parameters).data()
        if counts[0].get('counts') > 0:
            status = print("User " + str(uuid) + " is now a member of " + str(towner) + "'s "+ str(tname) + ".")
        else:
            status = print("[WARNING] User " + str(uuid) + " membership to " + str(tname) + " was not updated.")
        return status

    def remove_user_from_team(self, uuid:str, tname:str, towner:str):
        ''' This method is to remove a user from a team. '''
        parameters = {'uuid': uuid, 'tname': tname, 'towner':towner}
        cquery = '''
        MATCH (u:user {uuid:$uuid})-[rel:has_attr]->(t:Team {name:$tname, owner:$towner})
        WITH rel, count(rel) as counts
        CALL apoc.do.when(counts > 0,
            'DELETE rel RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {rel:rel, counts:counts}) YIELD value
        RETURN value.result AS result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User " + str(uuid) + " membership for " + str(towner) + "'s " + str(tname) + " was not updated.")
        else:
            status = print("User " + str(uuid) + " has been removed from " + str(towner) + "'s " + str(tname) + ".")
        return status

    ### CONTENT (MLExchange-Hosted Assets) and USER (unhosted, private) ASSETS ###
    def create_user_asset(self, name:str, owner:str, type:str, path:str):
        ''' Adds a customizable user asset after checking for existance of duplicates. Transaction-locked query.'''
        parameters = {'name': name, 'owner': owner, 'path': path, 'type': type}
        cquery = '''
        CALL {
                MATCH (ua:UserAsset {name:$name, owner:$owner, path:$path, type:$type})
                RETURN count(ua) AS counts
            }

        WITH counts
        CALL apoc.do.when(counts = 0,
            'CREATE (ua:UserAsset:Object:Primitive {uauid: toString((name)+toString(timestamp()))}) RETURN ua.uauid AS result',
            '',
            {counts:counts, name:$name}) YIELD value

        WITH value.result as ua_uid
        MATCH (u:user {uuid: $owner}), (ua:UserAsset {uauid:ua_uid})
        CREATE (u)-[:owner_of]->(ua)
        SET ua.name = $name, ua.owner = $owner, ua.path = $path, ua.type = $type
        RETURN ua_uid
        '''
        ua_uid = self.session.run(cquery, parameters=parameters).data()
        if ua_uid:
            status = print("User Asset ID " + str(ua_uid[0].get('ua_uid')) + " has been created!")
        else:
            status = print("[WARNING] User asset was not created.")
        return status
    
    def create_content_asset(self, name:str, owner:str, type:str, cuid:str, public=False):
        ''' Registers creation of new assets from content registry. Transaction-locked query.'''
        if public:
            parameters = {'name': name, 'owner': owner, 'type': type, 'cuid':cuid}
            cquery = '''
            CALL {
                MATCH (ca:content {cuid:$cuid})
                RETURN count(ca) AS counts
            }
                        
            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid})
            SET ca.name = $name, ca.owner = $owner, ca.type = $type, ca.public = True
            CREATE (u)-[:owner_of]->(ca)            
            RETURN ca.cuid as cauid
            '''
            ca_uid = self.session.run(cquery, parameters=parameters).data()
            if ca_uid:
                status = print("Public-flagged MLExchange Content has been registered: ID " + str(ca_uid[0].get('cauid')))
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " already has been registered. Contact Content Registry admin.")
            return status
        
        else:
            parameters = {'name': name, 'owner': owner, 'type': type, 'cuid':cuid}
            cquery = '''
            CALL {
                MATCH (ca:content {cuid:$cuid})
                RETURN count(ca) AS counts
            }
            WITH counts, $cuid AS c_uid
            CALL apoc.do.when(counts = 0,
                'CREATE (ca:content:Object:Primitive {cuid:c_uid}) RETURN ca.cuid AS result',
                '',
                {counts:counts, c_uid:c_uid}) YIELD value

            WITH value.result as ca_uid
            MATCH (u:user {uuid: $owner}), (ca:content {cuid:ca_uid})
            CREATE (u)-[:owner_of]->(ca)
            SET ca.name = $name, ca.owner = $owner, ca.type = $type, ca.public = False
            RETURN ca.cuid as cauid
            '''
            ca_uid = self.session.run(cquery, parameters=parameters).data()
            if ca_uid:
                status = print("Private-flagged MLExchange Content has been registered: ID " + str(ca_uid[0].get('cauid')))
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " already has been registered. Contact Content Registry admin.")
        return status

    def delete_user_asset(self, uauid=None, owner=None):
        """ Deletes user asset from graph database. Function for owner. """
        parameters = {'owner': owner, 'uauid': uauid}
        cquery = '''
        MATCH (ua:UserAsset {owner:$owner, uauid:$uauid})
        WITH count(ua) AS counts
        CALL apoc.do.when(counts > 0,
            'MATCH (ua:UserAsset {owner:$ua_owner, uauid:$ua_uid}) DETACH DELETE (ua) RETURN toInteger(1) AS result',
            'RETURN toInteger(0) AS result',
            {counts:counts, ua_owner:$owner, ua_uid:$uauid}) YIELD value
        RETURN value.result as result
        '''
        index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
        if index == 0:
            status = print("[WARNING] User Asset ID " + str(uauid) + " was not deleted.")
        if index == 1:
            status = print("User Asset ID " + str(uauid) + " has been removed from the database.")
        else:
            status = print("[WARNING] User Asset ID " + str(uauid) + " could not be found in database. Verify ID and try again.")
        return status
    
    def delete_content_asset(self, cuid=None):
        """ Deletes content asset from graph database. Function for Compute API, owner, and admin. """
        if cuid:
            parameters = {'cuid':cuid}
            cquery = '''
            MATCH (ca:content {cuid:$cuid})
            WITH count(ca) AS counts
            CALL apoc.do.when(counts > 0,
                'MATCH (c:content {cuid:$c_uid}) DETACH DELETE (c) RETURN toInteger(1) AS result',
                'RETURN toInteger(0) AS result',
                {counts:counts, c_uid:$cuid}) YIELD value
            RETURN value.result as result
            '''
            index = self.session.run(cquery, parameters=parameters).data()[0].get('result')
            if index == 0:
                status = print("[WARNING] Content ID " + str(cuid) + " was not deleted.")
            if index == 1:
                status = print("Content ID " + str(cuid) + " has been removed from the Content Registry.")
            else:
                status = print("[WARNING] Content ID " + str(cuid) + " could not be found in database. Verify ID and try again.")
        return status

    ### GET COMMANDS FOR RETRIEVING STORED DATABASE INFORMATION ###
    def get_userdb_metadata(self, active=True):
        """ Gets all information on active users (default). When "active" is false, returns ALL users. """
        if active:
            cquery = '''
            MATCH (up:UserProfile {active:True})
            RETURN up
            '''
            status = self.session.run(cquery).data()
        else:
            cquery = '''
            MATCH (up:UserProfile)
            RETURN up
            '''
            status = self.session.run(cquery).data()
        return [s['up'] for s in status]

    def get_user_metadata(self, uuid:str):
        """ Returns single user's metadata. """
        cquery = '''
        MATCH (up:UserProfile {uuid:$uuid})
        RETURN up
        '''
        status = self.session.run(cquery, parameters={'uuid':uuid}).data()
        return [s['up'] for s in status]

    def get_all_assets(self):
        cquery = '''
        MATCH (ca:content)
        RETURN ca AS asset
        UNION ALL
        MATCH (ua:UserAsset)
        RETURN ua AS asset
        '''
        status = self.session.run(cquery).data()
        return [s['asset'] for s in status]

    def get_all_roles(self):
        cquery = '''
        match (r:Role)
        return r
        '''
        status = self.session.run(cquery).data()
        return [s['r'] for s in status]

    def get_all_compute(self):
        cquery = '''
        match (comp:Compute)
        return comp
        '''
        status = self.session.run(cquery).data()
        return [s['cr'] for s in status]

    def get_all_teams(self):
        cquery = '''
        match (t:Team)
        return t
        '''
        status = self.session.run(cquery).data()
        return [s['t'] for s in status]

    def get_all_users(self, key_value=None):
        ''' This method will get all users including their profiles.
            The key will filter out irrelevant users.
            e.g. key = {'fname': 'Noah'} will return all users with Noah as their first name. '''
        cquery = '''
        match (up:UserProfile)
        return up
        '''
        status = self.session.run(cquery).data()

        # get active users
        users = []
        for s in status:
            if s['up']['active']: users.append(s['up'])
        
        # Filter users based on the key_value filter
        if key_value:
            users_filter = []
            for user in users:
                truth = True
                for k, v in key_value.items():
                    if user[k] != v: 
                        truth = False
                        break
                
                if truth: users_filter.append(user)
            
            return users_filter

        else:
            return users

    # Make policies
    def test_policy1(self):
        ''' Admin have full access of profiles. '''
        cquery = '''
        /// Policy 1 - Admin has full access to UserProfiles 
        match (admin:Role {name: 'Admin'})
        match (up:UserProfile)
        match (act:fullAccess {name:"Full Access"})
        create (pol:Policy {name: 'Policy1', decision: 'Permit'})
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:OBJ_CON]-(up)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status

    def test_policy2(self):
        cquery = '''
        /// Policy 2 - Admin and MLE Admin have full access to ALL Content 
        match (admin:Role {name: 'Admin'}), (mleadmin:Role {name: 'MLE Admin'})
        match (ca:content)
        match (act:fullAccess {name:"Full Access"})
        create (pol:Policy {name: 'Policy2', decision: 'Permit'})     
        merge (pol)<-[:SUB_CON]-(admin)
        merge (pol)<-[:SUB_CON]-(mleadmin)
        merge (pol)<-[:OBJ_CON]-(ca)
        merge (pol)<-[:ACT_CON]-(act);
        '''
        status = self.session.run(cquery)
        return status


if __name__ == '__main__':
    api = userAPI(url="bolt://44.201.1.101:7687", auth=("neo4j", "fans-hope-request"))

    ### For development purposes: creating sample db ###
    # Create neo4j AUTH DB roles
    #   api.create_role('Admin')
    #   api.create_role('MLE Admin')
    #   api.create_role('MLE User')
    #   api.create_role('General User')

    #   # Create actions
    #   def create_action():
    #       cquery = '''
    #       merge (read:Action {name:'Read'})-[:has_attr]->(fullAccess:Attribute:Group {name:"Full Access"})<-[:has_attr]-(write:Action {name:'Write'})
    #       '''
    #       api.session.run(cquery)

    #   create_action()

    #   # Create users and assign roles
    #   api.create_user('Howard', 'Yanxon', 'hg.yanxon@gmail.com', 'orcid')
    #   api.add_user_to_role('u_HYanxon00001','MLE Admin')
    #   api.create_user('Elizabeth', 'Holman', 'liz@gmail.com', 'orcid')
    #   api.add_user_to_role('u_EHolman00002','MLE Admin')
    #   api.create_user('Hari', 'Krish', 'krish@gmail.com', 'orcid')
    #   api.add_user_to_role('u_HKrish00003','Admin')
    #   api.create_user('John', 'Smith', 'smithj123@gmail.com', 'orcid')

    #   # Add compute location
    #   api.delete_compute(name='Aardvark', hostname='aardvark.anl.gov')
    #   api.create_compute(name='MLSandbox', hostname='mlsandbox.als.lbl.gov')
    #   api.add_user_to_compute(uuid='u_EHolman00002', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')
    #   api.add_user_to_compute(uuid='u_JSmith00004', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')
    #   api.remove_user_from_compute(uuid='u_EHolman00002', cname='MLSandbox', chostname='mlsandbox.als.lbl.gov')

    #   # Add Team
    #   api.delete_team(name='MLExchange_Team', owner='u_EHolman00002')
    #   api.create_team(name='MLExchange_Team', owner='u_EHolman00002')
    #   api.add_user_to_team(uuid='u_HKrish00003', tname='MLExchange_Team', towner='u_EHolman00002')
    #   api.remove_user_from_team(uuid='u_HKrish00003', tname='MLExchange_Team', towner='u_EHolman00002')

    #   # Create content assets
    #   api.create_content_asset(name='CAsset_00001', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid')
    #   api.delete_content_asset(cuid='2343462')
    #   api.create_content_asset(name='CAsset_00001', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid')
    #   api.delete_content_asset(cuid='placeholdcuid')
    #   api.create_content_asset(name='CAsset_00001', owner='u_HKrish00003', type='Trained_Model', cuid='placeholdcuid')

    #   # Create user assets
    #   api.create_user_asset(name='UAsset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
    #   api.create_user_asset(name='UAsset_00001', owner='u_HKrish00003', type='Trained_Model', path='HERE')
    #   ### Add two policies over which to check for permission.
    #   api.test_policy1()
    #   api.test_policy2()

    #   ### Check for blocking of node duplication on create_user_asset.
    #   #['u_HYanxon00001', 'u_EHolman00002', 'u_HKrish00003', 'u_JSmith00004']

    #   #self.archive_user(uuid='u_HKrish00003')

    #   #self.remove_user_content_asset(uuid='u_JSmith00004', from_master=True)
    #   #self.remove_user_content_asset(uuid='u_HYanxon00001', name='Asset_00001')
    #   
    #   # Check access of Smith (general user) to Write to Content
    #   # take account of owner!!!
    #   SmithWriteplaceholdcuid = {"SUBJECT_NAME_UID": "u_JSmith00004","OBJECT_NAME_UID": "placeholdcuid", "ACTION_NAME":"Write"}
    #   cypher_query = '''
    #   with $SmithWriteplaceholdcuid as req
    #   // Stage 1 - Subject Conditions
    #   match (sub:Subject {name:req.SUBJECT_NAME_UID})-[:HAS_ATTR*0..5]->(sc)-[:SUB_CON]->(pol:Policy)
    #   with req, pol, size(collect(distinct sc)) as sat_cons
    #   match (pol)<-[:SUB_CON]-(rc)
    #   with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons

    #   // Stage 2 - Object Conditions
    #   match (obj:Object {name:req.OBJECT_NAME_UID})-[:HAS_ATTR*0..5]->(sc)-[:OBJ_CON]->(pol) 
    #   with req, pol, size(collect(distinct sc)) as sat_cons
    #   match (pol)<-[:OBJ_CON]-(rc)
    #   with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons

    #   // Stage 3 - Action Conditions
    #   match (act:Action {name:req.ACTION_NAME})-[:HAS_ATTR*0..5]->(sc)-[:ACT_CON]->(pol) 
    #   with req, pol, size(collect(distinct sc)) as sat_cons
    #   match (pol)<-[:ACT_CON]-(rc)
    #   with req, pol, sat_cons, size(collect(rc)) as req_cons where req_cons = sat_cons 
    #   return case when count(pol) = 0 or 'Deny' in collect(pol.decision) then 'Deny' else 'Permit' end as decision
    #   '''
    #   results = api.session.run(cypher_query, SmithWriteplaceholdcuid=SmithWriteplaceholdcuid).data()
    #   print(results)

    users = api.get_all_users({'fname': 'Howard', 'lname': 'Yanxon'})
    for user in users:
        print(user)

    users = api.get_all_users({'email': 'smithj123@gmail.com'})
    for user in users:
        print(user)

    # Close session
    api.driver.close()

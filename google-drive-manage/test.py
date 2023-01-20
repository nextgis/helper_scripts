
from treelib import Node, Tree

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

import pprint,sys

class Gdrive_helper():
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)

        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()

        self.drive = GoogleDrive(self.gauth)
        
        self.target_user_email=None
        self.display_setting=None
        self.target_user_id = None
        
        self.pbar = None
        print('connect ok')


    ### Some basic helper functions ### 
    # populate gdrive structure in treelib tree object recurse
    
    def get_children(self,root_folder_id):
        str = "\'" + root_folder_id + "\'" + " in parents and trashed=false"
        file_list = self.drive.ListFile({'q': str}).GetList()
        return file_list

    def get_folder_id(self,root_folder_id, root_folder_title):
        file_list = self.get_children(root_folder_id)
        for file in file_list:
            if(file['title'] == root_folder_title):
                return file['id']

    def add_children_to_tree(self,tree, file_list, parent_id):
        #opening file or catalog here
        for file in file_list:
            node_name = file['title']
            if self.display_setting == 'users_emails':
                text = ''
                permissions = file.GetPermissions()
                for permission in permissions:
                    text+=' '+permission['id'] +': '+ permission['emailAddress']
                node_name+=text
                
            if self.display_setting == 'user_has_access':
                assert self.target_user_id is not None
                text = '***'
                permissions = file.GetPermissions()
                found = False
                for permission in permissions: 
                    if permission['id'] == self.target_user_id:
                        found = True
                if found:
                    text=' #'
                else:
                    text='  '
                node_name+=text          
                     
            if self.display_setting == 'revoke_user':
                assert self.target_user_id is not None
                text = '***'
                permissions = file.GetPermissions()
                found = False
                for permission in permissions: 
                    if permission['id'] == self.target_user_id:
                        found = True
                        file.DeletePermission(permission['id'])
                if found:
                    text=' deleted 1 permission'
                else:
                    text='  '
                node_name+=text                 
            tree.create_node(node_name, file['id'], parent=parent_id)
            # For debugging
            # print('parent: %s, title: %s, id: %s' % (parent_id, file['title'], file['id']))


    ### Go down the tree until you reach a leaf ###
    def populate_tree_recursively(self,tree,parent_id):
        print(".", end =' ') # <- no newline
        sys.stdout.flush() #<- makes python print it anyway
        children = self.get_children(parent_id)
        self.add_children_to_tree(tree, children, parent_id)
        if(len(children) > 0):
            for child in children:
                self.populate_tree_recursively(tree, child['id'])


    ### Create the tree and the top level node ###
    def get_tree(self,root_folder_id):
        print('wait for recursive read google drive tree start from dir '+root_folder_id)

        root_folder_title = root_folder_id

        tree = Tree()
        tree.create_node(root_folder_title, root_folder_id)
        self.populate_tree_recursively(tree, root_folder_id)

        print()
        tree.show()

    def revoke_user_from_tree(self):
        print('not implemented')
        
    def display_tree(self,root_folder_id):
          
        tree = self.get_tree(root_folder_id)
        
        
if __name__ == "__main__":

    gdrive_helper = Gdrive_helper()
    
    print('print permissions for tree')
    gdrive_helper.display_setting = 'users_emails'
    gdrive_helper.display_tree(root_folder_id='1LdEe244KSM9K0nVMdGEJs8IkaP_4MhtA')
    
    target_user_id = '06470162117676290615'
    print('print if user '+target_user_id+' has access')
    gdrive_helper.display_setting = 'user_has_access'
    gdrive_helper.target_user_id = target_user_id
    gdrive_helper.display_tree(root_folder_id='1LdEe244KSM9K0nVMdGEJs8IkaP_4MhtA')
     
    target_user_id = '06470162117676290615'
    print('delete permission for user '+target_user_id+' ')
    gdrive_helper.display_setting = 'revoke_user'
    gdrive_helper.target_user_id = target_user_id
    gdrive_helper.display_tree(root_folder_id='1LdEe244KSM9K0nVMdGEJs8IkaP_4MhtA')   

'''
for gdfile_list in drive.ListFile({'q': "'1U2ga3qTqeVKi5FiuFsb2M1u19wWIY5uC' in parents and trashed=false", 'maxResults': 10}): 
    for gdfile in gdfile_list:
        print(gdfile['title'])
        permissions = (gdfile.GetPermissions())
        for permission in permissions:
            print(' '+permission['id'].ljust(15) + permission['emailAddress'].rjust(50))
        print()
        
'''        

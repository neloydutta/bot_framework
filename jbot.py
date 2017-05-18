from jira import JIRA
import jira
# jiras = JIRA('https://jira.atlassian.com')
#
# authed_jira = JIRA(server='https://jira.atlassian.com', basic_auth=('neloy.dutta@gmail.com', 'laddu1993'))
from jira.exceptions import JIRAError


class JIRAClass:

    def __init__(self, jira_server, jira_user, jira_password):
        try:
            # log.info("Connecting to JIRA: %s" % jira_server)
            jira_options = {'server': jira_server}
            self.jira_obj = JIRA(options=jira_options,
                        # Note the tuple
                        basic_auth=(jira_user,
                                    jira_password))
        except Exception as e:
            print("Failed to connect to JIRA: %s" % e)

    def create_issue(self, project, summary, description, issue_name):
        issue_type = {}
        if issue_name:
            issue_type['name'] = issue_name
        return self.jira_obj.create_issue(project=project, summary=summary,
                                      description=description, issuetype=issue_type)

    def find_issue(self, id):
        try:
            issue = self.jira_obj.issue(id)
            issue_json = {}
            issue_json['id'] = issue.id
            issue_json['fields'] = {
                'project': issue.fields.project.name,
                'description': issue.fields.description,
                'status': issue.fields.status.name,
                'summary': issue.fields.summary,
                'votes': issue.fields.votes.votes,
                'labels': issue.fields.labels

            }
            issue_json['fields']['comments'] = []
            for comment in issue.fields.comment.comments:
                issue_json['fields']['comments'].append(comment.body)
            if issue.fields.reporter:
                issue_json['fields']['reporter'] = issue.fields.reporter.displayName
            if issue.fields.assignee:
                issue_json['fields']['assignee'] = issue.fields.assignee.displayName

            issue_json['watchers'] = []
            issue_watchers = self.jira_obj.watchers(issue.id)
            for watcher in issue_watchers.watchers:
                issue_json['watchers'].append(watcher.displayName)
            # print(issue.fields.worklog.)
            return issue_json

        except JIRAError as e:
            # print(e)
            return {
                'message': e.text
            }

    def find_projects(self):
        projects = self.jira_obj.projects()
        project_a = []
        for project in projects:
            project_j = {}
            project_j['name'] = project.name
            # if project.lead:
            #     project_j['lead'] = project.lead.displayName
            project_a.append(project_j)
        return project_a

    def my_issues(self):
        all_proj_issues = self.jira_obj.search_issues('project=SOMEKEY')
        my_issue_list = []
        for issue in all_proj_issues:
            if issue.fields.assignee is not None and issue.fields.assignee.key == self.jira_obj.myself()['key']:
                my_issue_list.append(self.find_issue(issue.id))
        return my_issue_list

def issue_json_to_str(issuej):
    return_str = ""
    for i in issuej.keys():
        if i == "fields":
            for field in issuej["fields"].keys():
                if type(issuej["fields"][field]) == str and issuej["fields"][field] != "":
                    return_str += field + ": "
                    return_str += issuej["fields"][field] + "\n"
                elif type(issuej["fields"][field]) == list and len(issuej["fields"][field]) > 0:
                    return_str += field + ": "
                    return_str += ", ".join(issuej["fields"][field]) + "\n"
        else:
            return_str += i + ": "
            if type(issuej[i]) == str:
                return_str += issuej[i] + "\n"
            elif type(issuej[i]) == list:
                return_str += ", ".join(issuej[i]) + "\n"
    return return_str


if __name__ == "__main__":
    njira = JIRAClass('http://localhost:8080/', 'adminuser', 'laddu1993')
    # cissue = njira.create_issue(project='SOMEKEY', summary='This is summary!', description='This is description!', issue_name='Bug')
    # print(njira.find_issue('SOMEKEY-10'))
    # print(njira.find_projects())
    # print(issue_json_to_str(njira.find_issue('SOMEKEY-10')))
    print(njira.my_issues())
"""Module for disabling GCP billing from Pub/Sub topic of a budget."""


import base64
import json
import os

from googleapiclient import discovery


PROJECT_ID = os.getenv('GCP_PROJECT')
PROJECT_NAME = f'projects/{PROJECT_ID}'


def disable_billing(data, context):
    if PROJECT_ID is None:
        raise KeyError('Environment variable "GCP_PROJECT" missing')

    pubsub_data = base64.b64decode(data['data']).decode('utf-8')
    pubsub_json = json.loads(pubsub_data)
    cost_amount = float(pubsub_json['costAmount'])
    budget_amount = float(pubsub_json['budgetAmount'])

    if cost_amount <= budget_amount:
        print(f'Costs {cost_amount} <= {budget_amount} budget, returning...')
        return

    print(f'Warning: Costs {cost_amount} > {budget_amount} budget, checking '
          'if billing is enabled...')
    billing = discovery.build('cloudbilling', 'v1', cache_discovery=False)
    projects = billing.projects()

    if __is_billing_enabled(PROJECT_NAME, projects):
        print('Billing is enabled, trying to disable...')
        __disable_billing_for_project(PROJECT_NAME, projects)
    else:
        print('Billing is already disabled - everything should be fine!')


def __is_billing_enabled(project_name, projects):
    """Determine whether billing is enabled for a project."""
    try:
        res = projects.getBillingInfo(name=project_name).execute()
        return res['billingEnabled']
    except KeyError:
        # If billingEnabled isn't part of the return, billing is not enabled
        return False
    except Exception as e:
        print('Unable to determine billing status, assuming it is enabled...')
        return True


def __disable_billing_for_project(project_name, projects):
    """Disable billing for a project by removing its billing account."""
    body = {'billingAccountName': ''}  # empty = disable billing
    try:
        res = (
            projects
            .updateBillingInfo(name=project_name, body=body)
            .execute()
        )
        print(f'Billing disabled successfully!\n\n{json.dumps(res)}')
    except Exception:
        print('Failed to disable billing, possibly check permissions and '
              'DISABLE BILLING MANUALLY ASAP!')

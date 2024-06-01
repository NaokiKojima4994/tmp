import boto3
from datetime import datetime
import argparse
import csv
import sys

# プロファイル名を指定
session = boto3.Session(profile_name='your_profile_name')

# AWS CodeCommitクライアントの作成
codecommit = session.client('codecommit')

def list_repositories():
    # リポジトリの一覧を取得
    response = codecommit.list_repositories()
    return [repo['repositoryName'] for repo in response['repositories']]

def list_pull_requests(repository_name):
    # 指定したリポジトリのプルリクエストの一覧を取得
    response = codecommit.list_pull_requests(
        repositoryName=repository_name,
        pullRequestStatus='OPEN'  # 必要に応じてステータスを変更
    )
    return response['pullRequestIds']

def get_pull_request_details(pull_request_id):
    # プルリクエストの詳細を取得
    response = codecommit.get_pull_request(
        pullRequestId=pull_request_id
    )
    return response['pullRequest']

def format_field(value, width):
    return str(value).ljust(width)

def generate_pr_url(repo_name, pr_id, region):
    return f"https://{region}.console.aws.amazon.com/codesuite/codecommit/repositories/{repo_name}/pull-requests/{pr_id}/details"

def main(args):
    repositories = list_repositories()
    
    # 初期値を設定
    repo_width = len("対象リポジトリ")
    pr_id_width = len("プルリクエストID")
    pr_title_width = len("プルリクエストタイトル")
    branch_width = len("マージ先ブランチ")
    user_width = len("作成者")
    date_width = len("作成日時")
    url_width = len("URL")

    # データ収集と幅の計算
    pr_data = []
    for repo in repositories:
        pull_request_ids = list_pull_requests(repo)
        for pr_id in pull_request_ids:
            pr_details = get_pull_request_details(pr_id)
            pr_title = pr_details['title']
            pr_created_by = pr_details['authorArn'].split('/')[-1]
            pr_creation_date = datetime.fromtimestamp(pr_details['creationDate']).strftime('%Y-%m-%d %H:%M:%S')
            pr_merge_base = pr_details['pullRequestTargets'][0]['destinationReference']
            pr_merge_head = pr_details['pullRequestTargets'][0]['sourceReference']
            pr_url = generate_pr_url(repo, pr_id, session.region_name)

            pr_data.append((repo, pr_id, pr_title, pr_merge_base, pr_merge_head, pr_created_by, pr_creation_date, pr_url))

            # 最大幅を更新
            repo_width = max(repo_width, len(repo))
            pr_id_width = max(pr_id_width, len(str(pr_id)))
            pr_title_width = max(pr_title_width, len(pr_title))
            branch_width = max(branch_width, len(pr_merge_base), len(pr_merge_head))
            user_width = max(user_width, len(pr_created_by))
            date_width = max(date_width

, len(pr_creation_date))
            url_width = max(url_width, len(pr_url))

    if args.csv:
        writer = csv.writer(sys.stdout)
        headers = ["対象リポジトリ", "プルリクエストID", "プルリクエストタイトル", "マージ先ブランチ", "マージ元ブランチ", "作成者", "作成日時"]
        if args.show_url:
            headers.append("URL")
        writer.writerow(headers)
        for data in pr_data:
            row = list(data[:7])
            if args.show_url:
                row.append(data[7])
            writer.writerow(row)
    else:
        # ヘッダーを表示
        header = (
            format_field("対象リポジトリ", repo_width) +
            format_field("プルリクエストID", pr_id_width) +
            format_field("プルリクエストタイトル", pr_title_width) +
            format_field("マージ先ブランチ", branch_width) +
            format_field("マージ元ブランチ", branch_width) +
            format_field("作成者", user_width) +
            format_field("作成日時", date_width)
        )
        if args.show_url:
            header += format_field("URL", url_width)
        print(header)
        print("=" * len(header))

        # データを表示
        for data in pr_data:
            row = (
                format_field(data[0], repo_width) +
                format_field(data[1], pr_id_width) +
                format_field(data[2], pr_title_width) +
                format_field(data[3], branch_width) +
                format_field(data[4], branch_width) +
                format_field(data[5], user_width) +
                format_field(data[6], date_width)
            )
            if args.show_url:
                row += format_field(data[7], url_width)
            print(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS CodeCommit Pull Request List Script")
    parser.add_argument("--show-url", action="store_true", help="プルリクエストのURLを表示します")
    parser.add_argument("--csv", action="store_true", help="CSV形式で標準出力します")
    args = parser.parse_args()
    main(args)
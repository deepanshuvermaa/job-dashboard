"""
Main Automation Workflow
Orchestrates GitHub monitoring, AI post generation, LinkedIn automation,
and Career-Ops pipeline (portal scanning, deduplication, evaluation, resume generation).
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_helper import db
from modules.github_service import GitHubService
from modules.ai_post_generator import AIPostGenerator
from modules.linkedin_job_scraper import LinkedInJobScraper
from modules.linkedin_poster import LinkedInPoster


class AutomationWorkflow:
    def __init__(self):
        self.github = GitHubService()
        self.ai_generator = AIPostGenerator()
        self.job_scraper = LinkedInJobScraper()
        self.linkedin_poster = LinkedInPoster()

        # Career-Ops modules (lazy-loaded)
        self._portal_scanner = None
        self._deduplicator = None
        self._evaluator = None
        self._batch_conductor = None
        self._resume_builder = None

    @property
    def portal_scanner(self):
        if not self._portal_scanner:
            from modules.portal_scanner import PortalScanner
            self._portal_scanner = PortalScanner()
        return self._portal_scanner

    @property
    def deduplicator(self):
        if not self._deduplicator:
            from modules.deduplication import JobDeduplicator
            self._deduplicator = JobDeduplicator()
        return self._deduplicator

    @property
    def evaluator(self):
        if not self._evaluator:
            from modules.job_evaluator import JobEvaluator
            self._evaluator = JobEvaluator()
        return self._evaluator

    @property
    def batch_conductor(self):
        if not self._batch_conductor:
            from modules.batch_conductor import BatchConductor
            self._batch_conductor = BatchConductor()
        return self._batch_conductor

    @property
    def resume_builder(self):
        if not self._resume_builder:
            from modules.resume_generator.resume_builder import ResumeBuilder
            self._resume_builder = ResumeBuilder()
        return self._resume_builder

    # ==================== Original Methods (unchanged) ====================

    def sync_repository_and_generate_posts(self, source_id: int, repo_name: str) -> List[int]:
        """
        Sync a GitHub repository and generate LinkedIn posts from recent activity
        Returns list of post IDs created
        """
        print(f"\n=== Syncing Repository: {repo_name} ===")

        try:
            # Get GitHub activity
            print("Fetching GitHub commits...")
            activity = self.github.get_repo_activity_summary(repo_name, days=7)

            if not activity['commits']:
                print("No recent commits found")
                return []

            print(f"Found {len(activity['commits'])} commits and {len(activity['pull_requests'])} PRs")

            # Generate posts for different pillars
            pillars = ['project_breakdown', 'learning_reflection', 'debugging_story']
            post_ids = []

            for pillar in pillars:
                if activity['commit_count'] < 2:
                    continue  # Need at least 2 commits for meaningful content

                print(f"\nGenerating {pillar} post...")
                post_data = self.ai_generator.generate_post_from_commits(
                    activity['commits'],
                    pillar=pillar
                )

                # Save to database
                post_id = db.add_post(
                    content=post_data['body'],
                    hooks=post_data['hooks'],
                    hashtags=post_data['hashtags'],
                    pillar=post_data['pillar'],
                    source_id=source_id
                )

                print(f"Created post ID: {post_id}")
                post_ids.append(post_id)

            # Update source sync timestamp and post count
            db.update_content_source(
                source_id,
                last_synced=datetime.now().isoformat(),
                post_count=db.get_content_sources()[0]['post_count'] + len(post_ids)
            )

            print(f"\n✓ Generated {len(post_ids)} posts from {repo_name}")
            return post_ids

        except Exception as e:
            print(f"Error syncing repository: {e}")
            return []

    def auto_sync_all_repos(self):
        """Automatically sync all active repositories"""
        print("\n" + "="*50)
        print("AUTO-SYNC: Checking all active repositories")
        print("="*50)

        sources = db.get_content_sources()
        active_sources = [s for s in sources if s['is_active']]

        print(f"Found {len(active_sources)} active repositories")

        total_posts = 0
        for source in active_sources:
            post_ids = self.sync_repository_and_generate_posts(
                source['id'],
                source['repo_name']
            )
            total_posts += len(post_ids)

        print(f"\n✓ Total posts generated: {total_posts}")
        return total_posts

    def auto_publish_approved_posts(self):
        """Automatically publish posts that are approved"""
        print("\n" + "="*50)
        print("AUTO-PUBLISH: Publishing approved posts")
        print("="*50)

        posts = db.get_posts(status='approved')

        if not posts:
            print("No approved posts to publish")
            return 0

        published_count = 0
        for post in posts:
            try:
                full_content = f"{post['hooks'][0]}\n\n{post['content']}"

                print(f"\nPublishing post {post['id']}...")
                result = self.linkedin_poster.create_post(
                    content=full_content,
                    hashtags=post['hashtags']
                )

                if result['success']:
                    db.update_post(
                        post['id'],
                        status='published',
                        published_at=datetime.now().isoformat(),
                        linkedin_url=result.get('post_url', '')
                    )
                    published_count += 1
                    print(f"✓ Published post {post['id']}")
                else:
                    print(f"✗ Failed to publish post {post['id']}: {result.get('error')}")

            except Exception as e:
                print(f"Error publishing post {post['id']}: {e}")

        self.linkedin_poster.close()

        print(f"\n✓ Published {published_count} posts")
        return published_count

    def auto_job_search_and_apply(
        self,
        keywords: str = "Software Engineer",
        location: str = "United States",
        max_applications: int = 10,
        easy_apply_only: bool = True
    ):
        """Automatically search and apply to jobs"""
        print("\n" + "="*50)
        print(f"AUTO-APPLY: Searching for '{keywords}' jobs")
        print("="*50)

        try:
            jobs = self.job_scraper.search_jobs(
                keywords=keywords,
                location=location,
                easy_apply=easy_apply_only,
                max_results=max_applications * 2
            )

            if not jobs:
                print("No jobs found")
                return 0

            print(f"Found {len(jobs)} jobs")

            easy_apply_jobs = [j for j in jobs if j['easy_apply']][:max_applications]

            print(f"Applying to {len(easy_apply_jobs)} Easy Apply jobs...")

            applied_count = 0
            for job in easy_apply_jobs:
                try:
                    print(f"\nApplying to: {job['title']} at {job['company']}")

                    result = self.job_scraper.apply_to_job(job['job_url'])

                    if isinstance(result, dict) and result.get('success'):
                        db.add_application(
                            job_title=job['title'],
                            company=job['company'],
                            location=job['location'],
                            job_url=job['job_url']
                        )
                        applied_count += 1
                        print(f"✓ Applied successfully")
                    else:
                        print(f"✗ Application failed")

                except Exception as e:
                    print(f"Error applying to job: {e}")

            self.job_scraper.close()

            print(f"\n✓ Applied to {applied_count}/{len(easy_apply_jobs)} jobs")
            return applied_count

        except Exception as e:
            print(f"Error in auto job apply: {e}")
            return 0

    # ==================== Career-Ops Pipeline ====================

    def full_career_ops_scan(
        self,
        include_linkedin: bool = True,
        linkedin_queries: List[str] = None,
        location: str = "United States",
        max_results_per_query: int = 50,
        auto_evaluate: bool = True,
        auto_generate_resumes: bool = False
    ) -> Dict:
        """
        Run the full career-ops pipeline:
        1. Scan all company career portals
        2. Run LinkedIn multi-query search
        3. Deduplicate across all sources
        4. Evaluate new jobs on 10 dimensions
        5. Generate tailored resumes for top jobs
        """
        print("\n" + "="*70)
        print("CAREER-OPS FULL PIPELINE")
        print("="*70)

        all_jobs = []

        # Step 1: Portal scan
        print("\n[1/5] Scanning company career portals...")
        try:
            portal_jobs = self.portal_scanner.scan_all_portals()
            all_jobs.extend(portal_jobs)
            print(f"Portal scan: {len(portal_jobs)} jobs found")
        except Exception as e:
            print(f"Portal scan error: {e}")
            portal_jobs = []

        # Step 2: LinkedIn search
        linkedin_jobs = []
        if include_linkedin and linkedin_queries:
            print(f"\n[2/5] LinkedIn multi-query search ({len(linkedin_queries)} queries)...")
            try:
                linkedin_jobs = self.job_scraper.search_jobs_multi(
                    queries=linkedin_queries,
                    location=location,
                    max_results_per_query=max_results_per_query
                )
                all_jobs.extend(linkedin_jobs)
                print(f"LinkedIn search: {len(linkedin_jobs)} jobs found")
            except Exception as e:
                print(f"LinkedIn search error: {e}")
        else:
            print("\n[2/5] LinkedIn search skipped")

        # Step 3: Deduplicate
        print(f"\n[3/5] Deduplicating {len(all_jobs)} jobs...")
        new_jobs, skipped = self.deduplicator.filter_new_jobs(all_jobs)
        print(f"Dedup: {len(new_jobs)} new, {skipped} duplicates skipped")

        # Save to database
        saved = 0
        for job in new_jobs:
            try:
                db.add_application(
                    job_title=job.get('title', 'Unknown'),
                    company=job.get('company', 'Unknown'),
                    location=job.get('location', 'Unknown'),
                    job_url=job.get('job_url', ''),
                    status='found',
                    salary_range=job.get('salary'),
                    notes=f"Source: {job.get('source', 'unknown')}"
                )
                saved += 1
            except:
                continue

        # Step 4: Evaluate
        evaluated_count = 0
        gate_passed = 0
        if auto_evaluate and new_jobs:
            print(f"\n[4/5] Evaluating {len(new_jobs)} new jobs...")
            evaluated = self.evaluator.evaluate_batch(new_jobs)
            evaluated_count = len(evaluated)
            gate_passed = sum(1 for j in evaluated if j.get('evaluation', {}).get('gate_pass', False))
            print(f"Evaluation: {gate_passed}/{evaluated_count} passed gate (C+ or above)")
        else:
            print("\n[4/5] Evaluation skipped")
            evaluated = new_jobs

        # Step 5: Generate resumes
        resumes_generated = 0
        if auto_generate_resumes and gate_passed > 0:
            print(f"\n[5/5] Generating resumes for top {min(gate_passed, 10)} jobs...")
            from modules.resume_generator.keyword_extractor import KeywordExtractor
            extractor = KeywordExtractor()

            top_jobs = [j for j in evaluated if j.get('evaluation', {}).get('gate_pass', False)][:10]
            for job in top_jobs:
                try:
                    keywords = extractor.extract(job.get('description_snippet', ''))
                    self.resume_builder.generate(job=job, keywords=keywords)
                    resumes_generated += 1
                except Exception as e:
                    print(f"Resume generation error: {e}")
        else:
            print("\n[5/5] Resume generation skipped")

        # Summary
        results = {
            'total_scraped': len(all_jobs),
            'portal_jobs': len(portal_jobs),
            'linkedin_jobs': len(linkedin_jobs),
            'duplicates_skipped': skipped,
            'new_jobs': len(new_jobs),
            'saved_to_db': saved,
            'evaluated': evaluated_count,
            'gate_passed': gate_passed,
            'resumes_generated': resumes_generated
        }

        print("\n" + "="*70)
        print("CAREER-OPS PIPELINE COMPLETE")
        print("="*70)
        for key, val in results.items():
            print(f"  {key}: {val}")
        print("="*70)

        return results

    def run_full_automation(self):
        """Run the complete automation workflow (original + career-ops)"""
        print("\n" + "="*70)
        print("STARTING FULL AUTOMATION WORKFLOW")
        print("="*70)

        # Step 1: Sync repositories and generate posts
        print("\n[1/4] Syncing GitHub repositories...")
        posts_generated = self.auto_sync_all_repos()

        # Step 2: Publish approved posts
        print("\n[2/4] Publishing approved posts...")
        posts_published = self.auto_publish_approved_posts()

        # Step 3: Search and apply to jobs
        print("\n[3/4] Searching and applying to jobs...")
        applications_sent = self.auto_job_search_and_apply(
            keywords="Python Developer",
            max_applications=5
        )

        # Step 4: Career-Ops pipeline
        print("\n[4/4] Running Career-Ops scan...")
        career_ops_results = {}
        try:
            career_ops_results = self.full_career_ops_scan(
                include_linkedin=False,  # Already searched in step 3
                auto_evaluate=True,
                auto_generate_resumes=False
            )
        except Exception as e:
            print(f"Career-Ops error: {e}")

        # Summary
        print("\n" + "="*70)
        print("AUTOMATION WORKFLOW COMPLETE")
        print("="*70)
        print(f"Posts Generated:      {posts_generated}")
        print(f"Posts Published:      {posts_published}")
        print(f"Applications Sent:    {applications_sent}")
        print(f"Portal Jobs Found:    {career_ops_results.get('portal_jobs', 0)}")
        print(f"New Jobs (deduped):   {career_ops_results.get('new_jobs', 0)}")
        print(f"Jobs Evaluated:       {career_ops_results.get('evaluated', 0)}")
        print(f"Gate Passed (C+):     {career_ops_results.get('gate_passed', 0)}")
        print("="*70)

        return {
            'posts_generated': posts_generated,
            'posts_published': posts_published,
            'applications_sent': applications_sent,
            'career_ops': career_ops_results
        }


def main():
    """Run automation from command line"""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Automation Workflow')
    parser.add_argument('--sync-repos', action='store_true', help='Sync GitHub repos')
    parser.add_argument('--publish-posts', action='store_true', help='Publish approved posts')
    parser.add_argument('--apply-jobs', action='store_true', help='Apply to jobs')
    parser.add_argument('--career-ops', action='store_true', help='Run career-ops pipeline')
    parser.add_argument('--full', action='store_true', help='Run full automation')

    args = parser.parse_args()

    workflow = AutomationWorkflow()

    if args.full:
        workflow.run_full_automation()
    elif args.sync_repos:
        workflow.auto_sync_all_repos()
    elif args.publish_posts:
        workflow.auto_publish_approved_posts()
    elif args.apply_jobs:
        workflow.auto_job_search_and_apply()
    elif args.career_ops:
        workflow.full_career_ops_scan(
            include_linkedin=True,
            linkedin_queries=["Software Engineer", "Python Developer", "Full Stack Developer"],
            auto_evaluate=True,
            auto_generate_resumes=True
        )
    else:
        print("Please specify an action. Use --help for options.")


if __name__ == "__main__":
    main()

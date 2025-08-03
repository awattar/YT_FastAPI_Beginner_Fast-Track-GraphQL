"""
Test GraphQL simple pagination functionality
"""
import pytest
from fastapi.testclient import TestClient

import models
from tests.factories import create_post_factory


class TestSimplePagination:
    """Test GraphQL posts pagination with simple page/limit approach"""
    
    def test_posts_pagination_first_page(self, test_client: TestClient, test_db_session):
        """Test first page of pagination"""
        # Create test posts
        PostFactory = create_post_factory(test_db_session)
        posts = PostFactory.create_batch(5)
        
        query = """
        query GetPosts($page: Int, $limit: Int) {
            posts(page: $page, limit: $limit) {
                posts {
                    id
                    title
                    content
                    author
                }
                pagination {
                    currentPage
                    totalPages
                    totalCount
                    hasNextPage
                    hasPreviousPage
                }
            }
        }
        """
        
        variables = {"page": 1, "limit": 3}
        response = test_client.post("/graphql/", json={"query": query, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        # Check response structure
        posts_data = data["data"]["posts"]
        assert len(posts_data["posts"]) == 3
        assert posts_data["pagination"]["currentPage"] == 1
        assert posts_data["pagination"]["totalPages"] == 2  # 5 posts / 3 per page = 2 pages
        assert posts_data["pagination"]["totalCount"] == 5
        assert posts_data["pagination"]["hasNextPage"] is True
        assert posts_data["pagination"]["hasPreviousPage"] is False
        
        # Verify posts are ordered by ID descending (newest first)
        post_ids = [int(post["id"]) for post in posts_data["posts"]]
        assert post_ids == sorted(post_ids, reverse=True)
    
    def test_posts_pagination_second_page(self, test_client: TestClient, test_db_session):
        """Test second page of pagination"""
        # Create test posts
        PostFactory = create_post_factory(test_db_session)
        posts = PostFactory.create_batch(5)
        
        query = """
        query GetPosts($page: Int, $limit: Int) {
            posts(page: $page, limit: $limit) {
                posts {
                    id
                    title
                }
                pagination {
                    currentPage
                    totalPages
                    totalCount
                    hasNextPage
                    hasPreviousPage
                }
            }
        }
        """
        
        variables = {"page": 2, "limit": 3}
        response = test_client.post("/graphql/", json={"query": query, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        posts_data = data["data"]["posts"]
        assert len(posts_data["posts"]) == 2  # Remaining 2 posts on second page
        assert posts_data["pagination"]["currentPage"] == 2
        assert posts_data["pagination"]["totalPages"] == 2
        assert posts_data["pagination"]["hasNextPage"] is False
        assert posts_data["pagination"]["hasPreviousPage"] is True
    
    def test_posts_pagination_empty_database(self, test_client: TestClient):
        """Test pagination with empty database"""
        query = """
        query GetPosts {
            posts {
                posts {
                    id
                }
                pagination {
                    currentPage
                    totalPages
                    totalCount
                    hasNextPage
                    hasPreviousPage
                }
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        posts_data = data["data"]["posts"]
        assert posts_data["posts"] == []
        assert posts_data["pagination"]["currentPage"] == 1
        assert posts_data["pagination"]["totalPages"] == 1
        assert posts_data["pagination"]["totalCount"] == 0
        assert posts_data["pagination"]["hasNextPage"] is False
        assert posts_data["pagination"]["hasPreviousPage"] is False
    
    def test_posts_pagination_default_values(self, test_client: TestClient, test_db_session):
        """Test pagination with default page and limit values"""
        # Create test posts
        PostFactory = create_post_factory(test_db_session)
        posts = PostFactory.create_batch(15)
        
        query = """
        query GetPosts {
            posts {
                posts {
                    id
                }
                pagination {
                    currentPage
                    totalPages
                    totalCount
                    hasNextPage
                    hasPreviousPage
                }
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        
        posts_data = data["data"]["posts"]
        # Default limit is 10
        assert len(posts_data["posts"]) == 10
        assert posts_data["pagination"]["currentPage"] == 1
        assert posts_data["pagination"]["totalPages"] == 2  # 15 posts / 10 per page = 2 pages
        assert posts_data["pagination"]["hasNextPage"] is True
        assert posts_data["pagination"]["hasPreviousPage"] is False


class TestPaginationErrorHandling:
    """Test error handling in simple pagination"""
    
    def test_invalid_page_argument(self, test_client: TestClient):
        """Test error handling for invalid page argument"""
        query = """
        query GetPosts($page: Int) {
            posts(page: $page) {
                posts { id }
            }
        }
        """
        
        variables = {"page": 0}
        response = test_client.post("/graphql/", json={"query": query, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "page must be >= 1" in str(data["errors"][0])
    
    def test_invalid_limit_argument(self, test_client: TestClient):
        """Test error handling for invalid limit argument"""
        query = """
        query GetPosts($limit: Int) {
            posts(limit: $limit) {
                posts { id }
            }
        }
        """
        
        variables = {"limit": 0}
        response = test_client.post("/graphql/", json={"query": query, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "limit must be >= 1" in str(data["errors"][0])
    
    def test_limit_too_high(self, test_client: TestClient):
        """Test error handling for limit exceeding maximum"""
        query = """
        query GetPosts($limit: Int) {
            posts(limit: $limit) {
                posts { id }
            }
        }
        """
        
        variables = {"limit": 101}
        response = test_client.post("/graphql/", json={"query": query, "variables": variables})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert "limit cannot exceed 100" in str(data["errors"][0])


class TestBackwardCompatibility:
    """Test that legacy allPosts query still works"""
    
    def test_all_posts_legacy_query(self, test_client: TestClient, test_db_session):
        """Test that legacy allPosts query still functions"""
        # Create test posts
        PostFactory = create_post_factory(test_db_session)
        posts = PostFactory.create_batch(3)
        
        query = """
        query GetAllPosts {
            allPosts {
                id
                title
                content
                author
            }
        }
        """
        
        response = test_client.post("/graphql/", json={"query": query})
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" not in data
        assert len(data["data"]["allPosts"]) == 3
        
        # Legacy query should return all posts without pagination
        returned_ids = {int(post["id"]) for post in data["data"]["allPosts"]}
        expected_ids = {post.id for post in posts}
        assert returned_ids == expected_ids
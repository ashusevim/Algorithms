#include<bits/stdc++.h>
using namespace std;

// Definition for a binary tree node
class Node {
public:
    int data;
    Node* left;
    Node* right;
    Node(int key) {
        data = key;
        left = right = nullptr;
    }
};

class Solution{
public:
	Node* createBinaryTree(){
		Node* root = new Node(1);
		root->left = new Node(2);
		root->right = new Node(3);
		root->left->left = new Node(4);
		root->left->right = new Node(5);
		root->right->left = new Node(6);
		root->right->right = new Node(7);
		return root;
	}
};

// Preorder traversal function
void preorder(Node* root) {
    if (root == nullptr) {
        return;
    } else {
        cout << root->data << '\n';  // Visit root
        preorder(root->left);        // Traverse left subtree
        preorder(root->right);       // Traverse right subtree
    }
}

void inorder(Node* root){
	if(root == nullptr){
		return;
	}
	else{
		inorder(root->left);
		cout << "after left: " << root->data << '\n';
		inorder(root->right);
		cout << "after right: " << root->data << '\n';
	}
}

void postorder(Node* root){
	if(root == nullptr)return;
	else{
		postorder(root->left);
		postorder(root->right);
		cout << root->data << '\n';
	}
}

//iterative way
void levelorderRecursive(Node* root){
	queue<Node*> qq;
	qq.push(root);
	while(!qq.empty()){
		int size = qq.size();
		for(int i = 0; i<size; i++){
			Node* node = qq.front();
			qq.pop();
			cout << node->data << '\n';
			if(node->left != nullptr)qq.push(node->left);
			if(node->right != nullptr)qq.push(node->right);
		}
	}
}

// recursive way
void levelorderRecursive(Node* root, int level){
	if(root == nullptr)return;

	if(level == 1){
		cout << root->data << '\n';
	}
	else{
		levelorderRecursive(root->left, level-1);
		levelorderRecursive(root->right, level-1);
	}
}

int main() {
	Solution solution;
	Node* root = solution.createBinaryTree();

	// preorder traversal
    // preorder(root);

    // postorder traversal
    // postorder(root);

    // inorder traversal
    // inorder(root);

    // levelorder(root);

    for(int i = 1; i<=7; i++){
   		levelorderRecursive(root, i);
    }

    return 0;
}

class TrieNode:
    def __init__(self):
        self.children = {} # 子节点详情
        self.is_end_of_word = False # 标记当前节点是否为单词结尾


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, current_node, word):
        # 从current_node处插入单词word
        for char in word:
            if char not in current_node.children:
                current_node.children[char] = TrieNode()
            current_node = current_node.children[char]
        current_node.is_end_of_word = True

    def search(self, word):
        # 判断单词是否存在于字典树，单词不在则插入
        current_node = self.root
        # 1. 单词存在后缀未在字典树里，则插入后缀
        for index, char in enumerate(word):
            if char not in current_node.children:
                self.insert(current_node, word[index:])
                return False
            current_node = current_node.children[char]
        # 2. 单词为字典树的子集，则插入单词结尾标记
        if not current_node.is_end_of_word:
            current_node.is_end_of_word = True
            return False
        # 3. 否则单词已在字典树中
        return True

    def starts_with(self, prefix):
        # 判断字典树是否存在前缀prefix
        current_node = self.root
        for char in prefix:
            if char not in current_node.children:
                return False
            current_node = current_node.children[char]
        return True

    def visualize(self):
        # 可视化字典树
        def _visualize_helper(f, node, level=0):
            if node.is_end_of_word:
                f.write("  " * level + str(level + 1) + "-<end>" + "\n")
            for char, child_node in node.children.items():
                f.write("  " * level + str(level + 1) + '-' + char + '\n')
                _visualize_helper(f, child_node, level + 1)
        
        with open("trie.txt", 'w', encoding='UTF8') as f:
            f.write("可视化字典树：\n\n")
            _visualize_helper(f, self.root)


if __name__ == '__main__':
    # 示例用法
    trie = Trie()

    print(trie.search("航天飞行器"))
    print(trie.search("航空航天"))
    print(trie.search("热气球"))
    print(trie.search("航空航天"))
    print(trie.search("航天飞行"))
    print(trie.search("航天飞行"))

    trie.visualize()

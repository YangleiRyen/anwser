/**
 * 动态分类筛选功能
 * 当选择问题分类筛选时，自动过滤问题列表
 */

(function($) {
    "use strict";
    
    // 确保DOM完全加载后初始化
    $(document).ready(function() {
        console.log('Dynamic category filter initialized');
        
        // 初始化所有行的分类筛选功能
        initDynamicCategoryFilter();
        
        // 监听新增问题行事件（Django admin formset事件）
        $(document).on('formset:added', function(event, $row) {
            // 给新增行一点时间渲染
            setTimeout(function() {
                initCategoryFilterForRow($row);
            }, 200);
        });
    });
    
    /**
     * 初始化所有行的分类筛选功能
     */
    function initDynamicCategoryFilter() {
        console.log('Initializing dynamic category filter for all rows');
        
        // 遍历所有问卷问题行
        $('.inline-related.surveyquestion_set').each(function() {
            var $inlineForm = $(this);
            
            // 查找所有表单行
            $inlineForm.find('tbody tr.form-row').each(function() {
                var $row = $(this);
                initCategoryFilterForRow($row);
            });
        });
    }
    
    /**
     * 初始化单行的分类筛选功能
     */
    function initCategoryFilterForRow($row) {
        console.log('Initializing category filter for row');
        
        // 查找当前行的分类筛选字段和问题选择字段
        var $categoryFilter = $row.find('.category-filter-select');
        var $questionSelect = $row.find('select[name*="question"]');
        
        // 确保找到元素
        if (!$categoryFilter.length || !$questionSelect.length) {
            console.log('Category filter or question select not found in row, skipping');
            return;
        }
        
        // 如果已经初始化过，跳过
        if ($row.data('category-filter-initialized')) {
            return;
        }
        
        // 标记为已初始化
        $row.data('category-filter-initialized', true);
        
        // 保存原始问题选项
        var $originalOptions = $questionSelect.find('option').clone();
        $row.data('original-question-options', $originalOptions);
        
        // 保存当前行的引用
        var currentRow = $row;
        
        // 分类筛选事件处理函数
        function onCategoryFilterChange() {
            var selectedCategory = $(this).val();
            console.log('Category filter changed to:', selectedCategory);
            
            // 获取当前行的问题选择字段
            var $currentQuestionSelect = currentRow.find('select[name*="question"]');
            
            // 应用分类筛选
            filterQuestionsByCategory($currentQuestionSelect, currentRow, selectedCategory);
        }
        
        // 绑定分类筛选事件
        $categoryFilter.off('change').on('change', onCategoryFilterChange);
    }
    
    /**
     * 根据选择的分类筛选问题
     */
    function filterQuestionsByCategory($questionSelect, $row, selectedCategory) {
        console.log('filterQuestionsByCategory called with category:', selectedCategory);
        
        // 获取原始问题选项
        var $originalOptions = $row.data('original-question-options');
        
        // 如果原始选项不存在或为空，重新获取
        if (!$originalOptions || $originalOptions.length === 0) {
            console.log('Original options not found, reloading from DOM');
            $originalOptions = $questionSelect.find('option').clone();
            $row.data('original-question-options', $originalOptions);
        }
        
        // 清空当前问题列表
        $questionSelect.empty();
        
        // 添加默认选项
        $questionSelect.append('<option value="">---------</option>');
        
        // 用于记录匹配的问题数量
        var matchedCount = 0;
        
        // 遍历所有原始选项，筛选符合条件的问题
        $originalOptions.each(function() {
            var $option = $(this);
            var optionText = $option.text();
            var optionValue = $option.val();
            
            // 跳过空选项
            if (optionValue === "") {
                return;
            }
            
            // 从问题选项文本中提取分类信息
            // 匹配格式：[分类ID:分类名称] 问题文本 (问题类型)
            var categoryRegex = /^\[([^:]+):([^\]]+)\]/;
            var categoryMatch = optionText.match(categoryRegex);
            
            // 初始化为不匹配
            var isMatch = false;
            
            // 如果找到了分类信息
            if (categoryMatch) {
                var questionCatId = categoryMatch[1];
                var questionCatName = categoryMatch[2];
                
                console.log('Question option:', optionText);
                console.log('Extracted category ID:', questionCatId);
                console.log('Selected category:', selectedCategory);
                
                // 比较分类ID
                if (selectedCategory === '' || selectedCategory === 'all') {
                    // 如果未选择分类或选择全部分类，显示所有问题
                    isMatch = true;
                } else if (String(questionCatId) === String(selectedCategory)) {
                    // 匹配分类ID，显示该问题
                    isMatch = true;
                }
            } else {
                // 没有分类信息的问题，只在未选择分类时显示
                if (selectedCategory === '' || selectedCategory === 'all') {
                    isMatch = true;
                }
            }
            
            // 如果匹配，添加到问题列表
            if (isMatch) {
                $questionSelect.append($option.clone());
                matchedCount++;
            }
        });
        
        console.log('Filter completed. Matched questions:', matchedCount);
        
        // 如果没有匹配的问题，添加提示
        if (matchedCount === 0 && selectedCategory !== '' && selectedCategory !== 'all') {
            $questionSelect.append('<option value="" disabled>该分类下没有问题</option>');
        }
    }
})(jQuery);
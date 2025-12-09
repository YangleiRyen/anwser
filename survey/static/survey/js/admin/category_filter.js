/**
 * 问卷问题分类筛选功能
 * 当选择分类时，自动过滤问题列表
 */

(function($) {
    "use strict";
    
    // 确保DOM完全加载后初始化
    $(document).ready(function() {
        console.log('Category filter script initialized');
        
        // 初始化所有问卷问题行
        initAllSurveyQuestionRows();
        
        // 监听新增问题行事件
        $(document).on('formset:added', function(event, $row) {
            setTimeout(function() {
                initSurveyQuestionRow($row);
            }, 100);
        });
        
        // 监听所有分类选择变化事件
        $(document).on('change', '.surveyquestion_set select[name*="category"]', function() {
            var $categorySelect = $(this);
            var $row = $categorySelect.closest('tr.form-row');
            var $questionSelect = $row.find('select[name*="question"]');
            
            // 获取选中的分类ID
            var selectedCategory = $categorySelect.val();
            console.log('Category changed to:', selectedCategory, 'in row:', $row.index());
            
            // 过滤问题列表
            filterQuestionsByCategory($row, $questionSelect, selectedCategory);
        });
    });
    
    /**
     * 初始化所有问卷问题行
     */
    function initAllSurveyQuestionRows() {
        console.log('Initializing all survey question rows');
        
        // 查找所有surveyquestion_set内联表单
        $('.inline-related.surveyquestion_set').each(function() {
            var $inlineForm = $(this);
            
            // 查找所有表单行
            $inlineForm.find('tbody tr.form-row').each(function() {
                var $row = $(this);
                initSurveyQuestionRow($row);
            });
        });
    }
    
    /**
     * 初始化单个问卷问题行
     */
    function initSurveyQuestionRow($row) {
        console.log('Initializing survey question row at index:', $row.index());
        
        // 查找当前行的分类选择字段和问题选择字段
        var $categorySelect = $row.find('select[name*="category"]');
        var $questionSelect = $row.find('select[name*="question"]');
        
        // 确保找到元素
        if (!$categorySelect.length || !$questionSelect.length) {
            console.log('Category or question select not found in row, skipping');
            return;
        }
        
        // 检查是否已经初始化
        if ($row.data('category-filter-initialized')) {
            console.log('Row already initialized, skipping');
            return;
        }
        
        // 标记为已初始化
        $row.data('category-filter-initialized', true);
        
        // 保存原始问题选项
        var $originalOptions = $questionSelect.find('option').clone();
        $row.data('original-question-options', $originalOptions);
        
        // 如果当前已经选择了分类，立即过滤问题列表
        var currentCategory = $categorySelect.val();
        console.log('Initial category value:', currentCategory, 'in row:', $row.index());
        // 无论是否选择分类，都执行过滤，处理未选择分类的情况
        filterQuestionsByCategory($row, $questionSelect, currentCategory);
    }
    
    /**
     * 根据选择的分类筛选问题
     */
    function filterQuestionsByCategory($row, $questionSelect, selectedCategory) {
        console.log('Filtering questions by category:', selectedCategory, 'in row:', $row.index());
        
        // 获取原始问题选项
        var $originalOptions = $row.data('original-question-options');
        
        // 如果原始选项不存在，重新获取
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
            
            // 跳过空选项和默认选项
            if (optionValue === "" || optionText === "---------" || optionText === "该分类下没有问题") {
                return;
            }
            
            // 从问题选项文本中提取分类信息
            // 匹配格式：[分类ID:分类名称] 问题文本 (问题类型)
            var categoryRegex = /^\[([^:]+):([^\]]+)\]/;
            var categoryMatch = optionText.match(categoryRegex);
            
            console.log('Processing option:', optionText, 'with value:', optionValue);
            
            // 初始化为不匹配
            var isMatch = false;
            
            // 处理不同的分类选择情况
            if (!selectedCategory || selectedCategory === "") {
                // 没有选择分类，显示所有问题
                isMatch = true;
                console.log('No category selected, showing all questions');
            } else if (selectedCategory === "none") {
                // 选择了"未分类"选项，只显示没有分类的问题
                isMatch = !categoryMatch;
                console.log('Selected "未分类" category, showing questions without category:', isMatch);
            } else {
                // 选择了具体分类，显示该分类下的问题
                if (categoryMatch) {
                    var questionCategoryId = categoryMatch[1];
                    var questionCategoryName = categoryMatch[2];
                    
                    console.log('Extracted category ID:', questionCategoryId, 'Name:', questionCategoryName);
                    console.log('Comparing with selected category:', selectedCategory);
                    
                    // 匹配分类ID
                    if (String(questionCategoryId) === String(selectedCategory)) {
                        isMatch = true;
                        console.log('Question matches selected category');
                    }
                }
            }
            
            // 如果匹配，添加到问题列表
            if (isMatch) {
                $questionSelect.append($option.clone());
                matchedCount++;
                console.log('Added question to list');
            }
        });
        
        console.log('Filter completed. Matched questions:', matchedCount, 'in row:', $row.index());
        
        // 如果没有匹配的问题，添加提示
        if (matchedCount === 0 && selectedCategory && selectedCategory !== "") {
            var noQuestionsText = selectedCategory === "none" ? "没有找到未分类的问题" : "该分类下没有问题";
            $questionSelect.append('<option value="" disabled>' + noQuestionsText + '</option>');
            console.log('No questions found for category:', selectedCategory);
        }
    }
})(django.jQuery);
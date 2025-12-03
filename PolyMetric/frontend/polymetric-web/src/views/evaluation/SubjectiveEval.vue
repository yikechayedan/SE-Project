<template>
  <div class="evaluation-page">
    <el-card class="eval-card" shadow="never">
      <template #header>
        <div class="card-header">
          <h2 class="title">主观评测</h2>
          <el-tag type="info">任务 ID: TASK-SUB-001</el-tag>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="input-card" shadow="hover">
            <template #header>
              <span class="section-title">问题 (Question)</span>
            </template>
            <blockquote class="prompt-text">
              我想了解文艺复兴时期的代表人物和主要成就。
            </blockquote>
            <p class="meta-info">数据集：历史知识库 | 类型：开放式问答</p>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="model-output-card" shadow="hover">
            <template #header>
              <span class="section-title">模型输出 (Model Output)</span>
            </template>
            <div class="model-response">
              <p>好的，文艺复兴 (约14世纪至17世纪) 是欧洲历史上一个思想、文化和艺术空前繁荣的时期，被称为"黑暗的中世纪"之后的重生。其核心精神是人文主义，即关注人本身、现实世界和古典文化，而非以中世纪那样一切以神为中心。</p>
              <p>以下是这一时期最杰出的代表人物及其主要成就，他们像群星一样照亮了那个时代。</p>
              <ol>
                <li><strong>列奥纳多·达·芬奇 — “全能天才”</strong><br>
                  艺术成就：《蒙娜丽莎》以其神秘的微笑和"晕涂法"技巧闻名于世，展现了人复杂的内心世界，《最后的晚餐》精确地捕捉了耶稣宣布被出卖时，十二门徒瞬间的戏剧性反应，在绘画和人物心理刻画上登峰造极。科学与其他成就：解剖学研究：通过解剖尸体，绘制了数百张极其精细的人体解剖图。运输时械：工程设计：在手稿中设计了直升机、坦克、潜水艇等超前概念的草图。科学研究：在光学、植物学、地质学等领域均有开创性研究。</li>
                <li><strong>米开朗基罗 — “神圣的雕塑家”</strong><br>
                  雕塑成就：《大卫》：用一整块大理石雕琢而成，完美展现了青年英雄的健美体魄、坚定意志和备战时的紧张感，成为佛罗伦萨精神的象征。《哀悼基督》：展现了圣母玛利亚的悲剧时刻的年轻、美丽与深沉哀伤。绘画成就：西斯廷教堂天顶画：历时四年独自完成，以《创世纪》为主题，绘制了数百个栩栩如生、姿态各异的巨大人形象，是人类艺术史上的不朽丰碑。建筑成就：主持设计了圣彼得大教堂的穹顶，成为罗马天际线的标志。</li>
              </ol>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="rating-card" shadow="always">
        <template #header>
          <span class="section-title rating-title">请对模型回复进行评测 (主观评分)</span>
        </template>
        
        <el-form :model="form">
          
          <el-form-item class ="comprehensive-score-item">
            <div class="score-labels-low">
                <span class="label-low">极差 (1)</span>
            </div>
            <el-radio-group v-model="form.comprehensive_score" class="round-rating-group">
              <el-radio-button 
                v-for="score in 10" 
                :key="score" 
                :label="score" 
                :value="score"
              >
                {{ score }}
              </el-radio-button>
            </el-radio-group>
            <div class="score-labels-high">
                <span class="label-high">优秀 (10)</span>
            </div>
          </el-form-item>

        </el-form>
      </el-card>
      
      <div class="navigation-footer">
        <div class="page-navigation">
            <el-button @click="handlePrevious">上一题</el-button>
        </div>
        
        <el-pagination
          layout="prev, pager, next"
          :total="100"
          :page-size="1"
          :current-page="12"
          :pager-count="11"
        />
        
        <div class="page-navigation">
            <el-button type="primary" @click="handleNext">下一题</el-button>
        </div>
      </div>

    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const score = ref(5)
</script>

<style scoped>
.subjective-eval { padding: 20px; max-width: 500px; margin: 0 auto; }
</style>
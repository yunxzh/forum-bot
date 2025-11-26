# backend/api/sites.py

@router.get("/sites")
async def list_sites():
    """获取所有站点"""
    pass

@router.post("/sites")
async def create_site(site: SiteCreate):
    """创建新站点"""
    pass

@router.put("/sites/{site_id}")
async def update_site(site_id: int, site: SiteUpdate):
    """更新站点配置"""
    pass

@router.delete("/sites/{site_id}")
async def delete_site(site_id: int):
    """删除站点"""
    pass

@router.get("/sites/presets")
async def get_presets():
    """获取预设模板列表"""
    return ["DeepFlood (Flarum架构)", "NodeLoc (Discourse架构)", "LinuxDo (Discourse架构)"]

@router.post("/sites/test-selectors")
async def test_selectors(site_config: dict):
    """测试 CSS 选择器是否有效"""
    pass
